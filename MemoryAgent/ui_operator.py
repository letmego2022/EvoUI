from playwright.sync_api import sync_playwright
import time
import random
import math
import re
import os
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import logging

logger = logging.getLogger(__name__)


class UIOperator:
    DEFAULT_VIEWPORT = {"width": 1280, "height": 720}   # {"width": 1920, "height": 1080}
    LOAD_TIMEOUT = 15000     
    NEW_PAGE_TIMEOUT = 5000  
    ACTION_WAIT_MS = 1000    

        # 【修改 1】初始化接收 config_data
    def __init__(self, target_url, config_data=None, headless=True, ignore_https_errors=True):
        self.config_data = config_data or {} # 存储配置数据
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        
        self.context = self.browser.new_context(
            viewport=self.DEFAULT_VIEWPORT,
            device_scale_factor=1,
            ignore_https_errors=ignore_https_errors
        )
        
        self.context.on("page", lambda page: page.set_viewport_size(self.DEFAULT_VIEWPORT))
        self.page = self.context.new_page() 
        
        if target_url:
            self.navigate_to(target_url)
    
    def extract_som(self):
        """获取最新页面元素"""
        self._focus_latest_page()
        self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        self.page.wait_for_load_state("networkidle", timeout=8000)
        self.page.wait_for_timeout(200)
        
        # 移除不稳定的硬等待 wait_for_timeout(300)

        js_path = os.path.join(os.path.dirname(__file__), "tools", "mark_page.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js_code = f.read()

        element_map = self.page.evaluate(js_code)

        som_list = []
        for _, v in element_map.items():
            bbox = v.get("bbox", {})
            x = bbox.get("x", 0)
            y = bbox.get("y", 0)
            w = bbox.get("width", 0)
            h = bbox.get("height", 0)

            cx = x + w / 2
            cy = y + h / 2

            som_list.append({
                "som_id": v.get("som_id"),
                "name": v.get("name"),
                "x": int(cx),
                "y": int(cy)
            })
        return som_list
    
    # 你需要在 UIOperator 类里增加这个辅助方法，以便复用
    def _type_by_coordinate(self, x, y, text_to_type):
        """通过坐标点击并输入的辅助方法（优化版）"""
        self.leave_visual_marker(x, y)
        self.page.mouse.click(x, y, delay=100) # 点击后稍微延迟，给页面反应时间
        
        # 移除不稳定的 time.sleep(0.5)
        
        # 清空操作
        self.page.keyboard.press("Control+A")
        self.page.keyboard.press("Backspace")
        
        # 【优化】使用 delay 参数模拟真实打字，这对于某些前端框架的输入监听更友好
        self.page.keyboard.type(text_to_type, delay=50) # 每个字符间隔50毫秒
        logger.info(f"   ✅ 输入成功 (通过坐标点击)")

     # ============================================================
    #  核心修改：参数解析器
    # ============================================================
    def _resolve_parameter(self, text):
        """
        检查 text 是否包含 <tag> 占位符，如果包含则替换为 config 中的真实值。
        支持: <username>, <password>, <zip_code> 等
        """
        if not text or not isinstance(text, str):
            return text
            
        # 正则匹配形如 <xxx> 的字符串
        match = re.match(r'^<(.*?)>$', text.strip())
        if match:
            tag = match.group(1) # 获取标签名，如 username
            
            # 1. 尝试从 credentials 找
            creds = self.config_data.get('credentials', {})
            if tag in creds:
                return str(creds[tag])
                
            # 2. 尝试从 business_data 找
            biz = self.config_data.get('business_data', {})
            if tag in biz:
                return str(biz[tag])
            return text # 找不到就返回原样
            
        return text # 不是占位符，返回原样

    # ============================================================
    #  核心：自动锁定最新标签页 (Silver Bullet)
    # ============================================================
    def _focus_latest_page(self):
        """
        【核心修复】
        检查浏览器当前的所有标签页。
        如果发现 `self.page` 不是最新的那个，或者有新标签页产生，
        强制将控制权切换到列表中的最后一个页面。
        """
        pages = self.context.pages
        if not pages: return

        latest_page = pages[-1]
        
        # 如果当前指针不等于最新页面，或者最新页面没在最前
        if self.page != latest_page:
            logger.info(f"   ⚡ [自动切换] 检测到新标签页，切换焦点: {latest_page.title()[:20]}...")
            self.page = latest_page
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=3000)
                self.page.set_viewport_size(self.DEFAULT_VIEWPORT)
                self.page.bring_to_front()
            except:
                pass
        else:
            # 即使是同一个页面，也确保它在前台
            try:
                self.page.bring_to_front()
            except:
                pass
    
    def navigate_to(self, url):
        if not url: raise ValueError("URL不能为空")
        self.page.goto(url, wait_until='domcontentloaded', timeout=self.LOAD_TIMEOUT)
        self.page.set_viewport_size(self.DEFAULT_VIEWPORT)
        # goto 已经等待了，通常不再需要额外的等待

    def go_back(self):
        """执行浏览器后退操作"""
        logger.info("[操作] 执行浏览器后退 (Go Back)")
        self.page.go_back()
        try:
            self.page.wait_for_load_state("load", timeout=self.LOAD_TIMEOUT)
        except Exception:
            pass
        self.page.wait_for_timeout(1500)

    def refresh(self):
        """刷新当前页面"""
        logger.info("[操作] 刷新页面 (Refresh)")
        self.page.reload()
        try:
            self.page.wait_for_load_state("load", timeout=self.LOAD_TIMEOUT)
        except:
            pass
        self.page.wait_for_timeout(1500)

    def scroll(self, direction="down", magnitude=500):
        """页面滚动"""
        logger.info(f"[操作] 页面滚动: {direction}, 幅度: {magnitude}")
        if direction == "down":
            self.page.mouse.wheel(0, magnitude)
        elif direction == "up":
            self.page.mouse.wheel(0, -magnitude)
        time.sleep(0.5)

    def screenshot(self, path):
        """
        截图前强制锁定最新页面，并等待页面稳定以消除抖动。
        """
        # 1. 锁定最新页面 (保留原有逻辑)
        self._focus_latest_page()
        self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        self.page.screenshot(
            path=path,
            full_page=False,
            animations="disabled",
            caret="hide"
        )

    def close(self):
        logger.info("[操作] 关闭浏览器...")
        if hasattr(self, 'browser') and self.browser.is_connected():
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()

    def norm_to_pixel(self, x, y):
        """
        支持：
        1. 归一化坐标 (0~1)，相对于浏览器 viewport
        2. 模型像素坐标 (0~1024)，模型输入为 1024x1024，无 padding
        3. 浏览器像素坐标（兜底）

        模型坐标 -> 浏览器坐标 使用非等比反缩放
        """

        viewport = self.page.viewport_size
        vw = viewport['width'] if viewport else self.DEFAULT_VIEWPORT['width']
        vh = viewport['height'] if viewport else self.DEFAULT_VIEWPORT['height']

        # -------- Case 1：归一化坐标 --------
        if 0 <= x <= 1 and 0 <= y <= 1:
            px = int(x * vw)
            py = int(y * vh)
            return px, py

        # -------- Case 2：模型像素坐标 (1024x1024) --------
        if 0 <= x <= 1024 and 0 <= y <= 1024:
            scale_x = 1024 / vw
            scale_y = 1024 / vh

            px = int(x / scale_x)
            py = int(y / scale_y)

            return px, py

        # -------- Case 3：直接当浏览器像素 --------
        px = int(x)
        py = int(y)
        return px, py


    def highlight_point(self, x, y):
        js = f"""(() => {{
            const dot = document.createElement('div');
            dot.style.cssText = `position: fixed; left: {x-5}px; top: {y-5}px; width: 10px; height: 10px; background: red; border-radius: 50%; z-index: 99999; pointer-events: none;`;
            document.body.appendChild(dot);
            setTimeout(() => dot.remove(), 1000);
        }})()"""
        try: self.page.evaluate(js)
        except: pass

    def leave_visual_marker(self, x, y):
        js = f"""(() => {{
            const old = document.getElementById('ai-feedback-marker');
            if (old) old.remove();
            const marker = document.createElement('div');
            marker.id = 'ai-feedback-marker';
            marker.style.cssText = `position: fixed; left: {x-10}px; top: {y-10}px; width: 20px; height: 20px; border: 2px solid red; background-color: rgba(255,0,0,0.2); border-radius: 50%; z-index: 2147483647; pointer-events: none;`;
            marker.innerHTML = `<div style="position:absolute; left:9px; top:0; width:2px; height:20px; background:red;"></div><div style="position:absolute; left:0; top:9px; width:20px; height:2px; background:red;"></div>`;
            document.body.appendChild(marker);
        }})()"""
        try: self.page.evaluate(js)
        except: pass

    def clear_marker(self):
        try: self.page.evaluate("const el = document.getElementById('ai-feedback-marker'); if(el) el.remove();")
        except: pass

    def human_like_swipe(self, x1, y1, x2, y2):
        self.page.mouse.move(x1, y1)
        time.sleep(random.uniform(0.1, 0.3))
        self.page.mouse.down()
        time.sleep(random.uniform(0.05, 0.15))
        steps = 10
        for i in range(steps):
            mx = x1 + (x2 - x1) * (i + 1) / steps
            my = y1 + (y2 - y1) * (i + 1) / steps
            self.page.mouse.move(mx, my)
            time.sleep(0.02)
        self.page.mouse.up()
    
    def find_closest_som(
        self,
        x,
        y,
        som_list,
        max_distance_px=40,   # 🔴 核心参数：最大允许收敛距离（像素）
    ):
        """
        返回距离 (x, y) 最近的 SoM
        - 如果最近 SoM 距离超过阈值，则忽略收敛
        """
        if not som_list:
            return {"x": x, "y": y}

        min_dist_sq = float("inf")
        closest = None

        for som in som_list:
            dx = x - som.get("x", x)
            dy = y - som.get("y", y)
            dist_sq = dx * dx + dy * dy

            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest = som

        # 🔴 距离判断
        if min_dist_sq > max_distance_px * max_distance_px:
            # 距离太远，不可信
            return {"x": x, "y": y}

        return closest


    # ============================================================
    #  执行逻辑
    # ============================================================

    def execute_action(self, action_json, som_list=None):
        if not isinstance(action_json, dict): return

        # 1. 动作执行前，先确保我们在操作最新的页面
        self._focus_latest_page()

        action = action_json.get("action")
        coordinate = action_json.get("coordinate", {})
        
        try:
            if action == "click":
                coordinate = action_json.get("coordinate", {})
                x, y = self.norm_to_pixel(coordinate.get('x', 0), coordinate.get('y', 0))
                logger.info(f"[操作] 准备点击坐标 ({x}, {y}) 附近...")

                click_x, click_y = x, y # 默认使用原始坐标

                # 如果有 SoM 列表，则进行坐标收敛
                if som_list:
                    closest_som = self.find_closest_som(x, y, som_list)
                    click_x = closest_som['x']
                    click_y = closest_som['y']
                    logger.info(f"   🔹 SoM 收敛 -> 精确坐标: ({click_x}, {click_y})")
                else:
                    logger.warning("   ⚠️ 无 SoM 列表，使用原始坐标。")

                # 标记并执行点击
                self.leave_visual_marker(click_x, click_y)
                self.page.mouse.click(click_x, click_y)
                logger.info(f"   ✅ 点击成功 @ ({click_x}, {click_y})")

                # 点击完成后，等待页面响应稳定
                logger.info("   -> 点击完成，等待页面响应...")
                try:
                    self.page.wait_for_load_state("networkidle", timeout=10000)
                except PlaywrightTimeoutError:
                    logger.warning("点击后等待 'networkidle' 超时，页面可能仍在后台加载或为纯前端更新。")


            # ==========================================================
            #  分支：Type (纯坐标版)
            # ==========================================================
            elif action == "type":
                coordinate = action_json.get("coordinate", {})
                x, y = self.norm_to_pixel(coordinate.get('x', 0), coordinate.get('y', 0))

                raw_text = action_json.get("text", "")
                final_text = self._resolve_parameter(raw_text)
                log_text = raw_text if final_text != raw_text else final_text
                logger.info(f"[操作] 准备向坐标 ({x}, {y}) 附近输入: {log_text}")

                type_x, type_y = x, y # 默认使用原始坐标

                # 如果有 SoM 列表，则进行坐标收敛
                if som_list:
                    closest_som = self.find_closest_som(x, y, som_list)
                    type_x = closest_som['x']
                    type_y = closest_som['y']
                    logger.info(f"   🔹 SoM 收敛 -> 精确坐标: ({type_x}, {type_y})")
                else:
                    logger.warning("   ⚠️ 无 SoM 列表，使用原始坐标。")

                # 直接调用坐标输入辅助方法
                self._type_by_coordinate(type_x, type_y, final_text)

            elif action == "wait":
                time.sleep(action_json.get("duration_ms", 1000) / 1000)

            elif action == "scroll":
                direction = action_json.get("direction", "down")
                # magnitude = action_json.get("magnitude")
                self.scroll(direction)
            
            elif action == "go_back":
                self.go_back()
                
            elif action == "refresh":
                self.refresh()
            
            # ---------------------------
            # 4. Press Key (按键) - 增强版
            # ---------------------------
            elif action == "press_key":
                key = action_json.get("key")
                repeat_count = action_json.get("repeat", 1) # 默认为 1 次
                
                logger.info(f"[操作] 按键: {key} (重复 {repeat_count} 次)")
                
                # 循环执行按键
                for _ in range(repeat_count):
                    self.page.keyboard.press(key)
                    # 极短的间隔，模拟真实按键速度
                    time.sleep(0.05) 
                
            elif action == "hover":
                x, y = self.norm_to_pixel(coordinate.get('x', 0), coordinate.get('y', 0))
                 # 匹配最近的 SoM
                if som_list is not None:
                    closest_som = self.find_closest_som(x, y, som_list)
                    x, y = closest_som['x'], closest_som['y']
                    logger.info(f"[操作] 点击坐标 (匹配最近 SoM): ({x}, {y})")
                self.leave_visual_marker(x, y)
                self.page.mouse.move(x, y)
                
            elif action == "swipe":
                start = action_json.get("start", {})
                end = action_json.get("end", {})
                x1, y1 = self.norm_to_pixel(start.get('x', 0), start.get('y', 0))
                x2, y2 = self.norm_to_pixel(end.get('x', 0), end.get('y', 0))
                self.leave_visual_marker(x1, y1)
                self.human_like_swipe(x1, y1, x2, y2)

            # time.sleep(self.ACTION_WAIT_MS / 1000)

        except Exception as e:
            logger.error(f"[异常] 执行操作 '{action}' 时出错: {e}")

    def check_completion_criteria(self, step_description):
        self._focus_latest_page() # 检查前也确保是最新页面
        current_url = self.page.url
        if "登录" in step_description and ("login" not in current_url.lower()):
            return True
        return False