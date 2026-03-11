from ui_operator import UIOperator
import threading
import queue
import time
import logging

logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self):
        self.operator = None
        self.lock = threading.RLock()
        # 移除 self.current_url，因为 URL 是动态变化的，存这里没意义

    def start_browser(self, url, config_data=None):
        """启动浏览器并访问指定URL"""
        logger.info(f"Attempting to start browser for URL: {url}")
        with self.lock:
            # 确保在创建新实例前，旧实例已被清理
            self._internal_close() 
            try:
                # 创建新的浏览器实例
                # 建议 headless=False 以便调试观察
                self.operator = UIOperator(target_url=None,config_data=config_data,  # <--- 关键传参
                 headless=True) 
                logger.debug("UIOperator instance created.")
                
                # 导航
                self.operator.navigate_to(url)
                logger.info(f"Browser started and navigated to {url}")
                 # ==========================================
                # 【修正方案】使用 JS 设置缩放
                # ==========================================
                # try:
                #     # 1. 不要点击 body，直接注入 JS
                #     # 2. 设置 '0.8' 即 80%
                #     # 3. 对 html 标签设置通常比对 body 更稳健
                #     logger.info("🎨 Setting page zoom to 85%...")
                #     self.operator.page.evaluate("document.body.style.zoom = '0.85'")
                    
                #     # 备选：如果有些网站 body zoom 不生效，可以尝试 transform（通常不需要）
                #     # self.operator.page.evaluate("document.body.style.transform = 'scale(0.8)'; document.body.style.transformOrigin = '0 0';")
                # except Exception as z_err:
                #     logger.warning(f"⚠️ Failed to set zoom: {z_err}")
                # ==========================================
                return True, "浏览器启动成功"
            except Exception as e:
                error_msg = f"启动浏览器失败: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self._internal_close() 
                return False, error_msg

    def get_operator(self):
        """获取当前浏览器操作器"""
        with self.lock:
            # 这里的 operator 是一个引用。
            # 即使 ui_operator 内部切换了 self.page，这里获取到的对象依然是最新的。
            return self.operator

    def _internal_close(self):
        """内部关闭逻辑"""
        if self.operator:
            try:
                logger.debug("Attempting to close UIOperator...")
                self.operator.close()
                logger.debug("UIOperator closed successfully.")
            except Exception as e:
                logger.warning(f"Error closing operator: {e}")
            finally:
                self.operator = None

    def close_operator(self):
        """关闭浏览器"""
        logger.info("Close operator requested.")
        with self.lock:
            self._internal_close()
        logger.info("Close operator completed.")

    def is_browser_running(self):
        """检查浏览器是否正在运行"""
        with self.lock:
            return self.operator is not None

# 全局单例
browser_manager = BrowserManager()

# --- 任务队列相关 (保持原样，用于异步任务) ---
task_queue = queue.Queue()
browser_thread = None
browser_thread_running = False

def browser_worker():
    global browser_thread_running
    logger.info("Browser worker thread started.")
    while browser_thread_running:
        try:
            task = task_queue.get(timeout=1)
            if task is None:
                task_queue.task_done()
                break
            func, args, kwargs, callback = task
            try:
                result = func(*args, **kwargs)
                if callback: callback(result, None)
            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)
                if callback: callback(None, e)
            finally:
                task_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"Worker critical: {e}")
    logger.info("Browser worker thread stopped.")

def start_browser_thread():
    global browser_thread, browser_thread_running
    if not browser_thread_running or browser_thread is None or not browser_thread.is_alive():
        browser_thread_running = True
        browser_thread = threading.Thread(target=browser_worker, daemon=True)
        browser_thread.start()

def stop_browser_thread():
    global browser_thread, browser_thread_running
    if browser_thread_running:
        browser_thread_running = False
        task_queue.put(None)
        if browser_thread:
            browser_thread.join(timeout=2)
            browser_thread = None

def execute_in_browser_thread(func, *args, callback=None, **kwargs):
    start_browser_thread()
    task_queue.put((func, args, kwargs, callback))

# --- 全局函数接口 (供 main.py 调用) ---

def start_browser(url, config_data=None):
    return browser_manager.start_browser(url, config_data=config_data)

def get_operator():
    return browser_manager.get_operator()

# 【关键修复】增加 *args, **kwargs 以兼容 signal 信号调用
def close_operator(*args, **kwargs):
    """
    全局函数接口：关闭浏览器。
    支持接收 signal 参数 (signum, frame) 以便作为信号处理回调。
    """
    if args:
        logger.info(f"Signal received (e.g., Ctrl+C), closing browser...")
    else:
        logger.info("Global close_operator() called.")
        
    browser_manager.close_operator()

def is_browser_running():
    return browser_manager.is_browser_running()