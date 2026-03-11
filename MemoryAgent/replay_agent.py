import os
import time
import json
import logging

# 复用你现有的模块
from global_operator import start_browser, get_operator, close_operator
from subagent.critic_agent import verify_step_success
from subagent.report_manager import ReportManager

# 【新增】导入 AI 执行所需的模块
from utils import analyze_local_image, parse_json_safely
from subagent.prompt import ui_auto_prompt

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [Replay] %(message)s')
logger = logging.getLogger("ReplayAgent")

class ReplayAgent:
    def __init__(self, json_path):
        """
        :param json_path: 录制好的 scenario_xxxx.json 文件路径
        """
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"找不到场景文件: {json_path}")
        
        self.json_path = json_path # 记录路径以便更新
        
        with open(json_path, 'r', encoding='utf-8') as f:
            self.scenario_data = json.load(f)
            
        self.task_description = self.scenario_data.get("task_description", "Unknown Task")
        self.target_url = self.scenario_data.get("target_url", "")
        
        # 初始化报告管理器
        self.reporter = ReportManager()
        self.reporter.set_task(f"[REPLAY+HEAL] {self.task_description}")
        
        logger.info(f"📂 加载场景成功: {self.task_description}")

    def _save_scenario(self):
        """将修复后的数据回写到 JSON"""
        try:
            # 更新时间戳
            self.scenario_data["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(self.scenario_data, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 自愈成功！场景文件已更新: {self.json_path}")
        except Exception as e:
            logger.error(f"❌ 保存场景失败: {e}")

    def _heal_step(self, operator, step_key, step_desc):
        """
        【自愈核心】当回放失败时，调用 AI 重新执行并修正
        """
        logger.warning(f"🚑 启动自愈模式 (Self-Healing) - 步骤 {step_key}")
        
        # 限制重试次数，防止死循环
        max_retries = 2
        retry_count = 0
        
        while retry_count < max_retries:
            retry_count += 1
            
            # 1. 截图
            abs_path, rel_path = self.reporter.get_new_screenshot_path(tag=f"step{step_key}_heal_try{retry_count}")
            operator.screenshot(abs_path)
            
            # 2. 构造 Prompt
            full_prompt = (
                f"{ui_auto_prompt}\n"
                f"【任务】{self.task_description}\n"
                f"【当前目标】{step_desc}\n"
                f"注意：之前的操作失败了，请重新分析页面状态，生成新的操作。"
            )
            
            # 3. Executor 思考
            try:
                ai_response, usage = analyze_local_image(abs_path, full_prompt)
                actions = parse_json_safely(ai_response)
                self.reporter.log_vision_attempt(retry_count, rel_path, full_prompt, ai_response, actions, token_usage=usage)
            except Exception as e:
                logger.error(f"AI Error: {e}")
                continue

            if not actions:
                continue

            # 4. 执行新动作
            executed_actions = []
            
            # Case A: AI 认为直接完成了 (Pass-through)
            if isinstance(actions, dict) and actions.get("status") == "completed":
                logger.info("   🤖 AI 认为无需操作，直接验证...")
            
            # Case B: AI 生成动作列表
            elif isinstance(actions, list):
                for act in actions:
                    try:
                        logger.info(f"   🔧 [自愈] 执行: {act.get('action')}")
                        operator.execute_action(act)
                        executed_actions.append(act)
                    except:
                        pass
                time.sleep(2)

            # 5. Critic 验证
            check_path, check_rel = self.reporter.get_new_screenshot_path(tag=f"step{step_key}_heal_check_{retry_count}")
            operator.screenshot(check_path)
            
            is_success, reason, c_usage = verify_step_success(check_path, self.task_description, step_desc)
            self.reporter.log_critic_check(check_rel, is_success, f"[Healed] {reason}", token_usage=c_usage)
            
            if is_success:
                logger.info(f"   ✅ 自愈成功: {reason}")
                
                # 【关键】更新内存中的数据
                self.scenario_data["steps"][step_key]["actions"] = executed_actions
                self.scenario_data["steps"][step_key]["assertion"] = reason
                
                # 【关键】写入磁盘
                self._save_scenario()
                
                return True
            else:
                logger.warning(f"   ❌ 自愈尝试失败: {reason}")
        
        return False

    def run(self):
        logger.info(f"🚀 开始回放，目标 URL: {self.target_url}")
        
        if not self.target_url:
            logger.error("❌ JSON 中缺少 target_url，无法启动")
            return

        start_browser(self.target_url)
        operator = get_operator()
        time.sleep(3)

        steps_map = self.scenario_data.get("steps", {})
        sorted_keys = sorted(steps_map.keys(), key=lambda x: int(x))
        
        all_passed = True

        for step_key in sorted_keys:
            step_data = steps_map[step_key]
            step_desc = step_data.get("description")
            old_actions = step_data.get("actions", [])
            
            logger.info(f"\n🔵 === 回放步骤 {step_key}: {step_desc} ===")
            self.reporter.log_step_start(step_key, len(sorted_keys), f"[Replay] {step_desc}")

            # 标记当前步骤是否需要自愈
            need_healing = False

            # --- A. 尝试执行历史动作 ---
            if old_actions:
                for i, act in enumerate(old_actions):
                    logger.info(f"   ▶ 执行动作 {i+1}: {act.get('action')}")
                    try:
                        operator.execute_action(act)
                    except Exception as e:
                        logger.error(f"   ❌ 动作执行异常: {e}")
                        need_healing = True # 动作报错，直接触发自愈
                        break 
                if not need_healing:
                    time.sleep(2)
            else:
                logger.info("   ⏩ 无需操作，直接校验...")
                time.sleep(1)

            # --- B. 校验 (如果动作没报错) ---
            if not need_healing:
                logger.info("   ⚖️ 呼叫 Critic 进行视觉验收...")
                check_path, check_rel = self.reporter.get_new_screenshot_path(tag=f"step{step_key}_replay_check")
                operator.screenshot(check_path)
                
                is_success, reason, usage = verify_step_success(
                    screenshot_path=check_path,
                    global_goal=self.task_description,
                    current_step_desc=step_desc
                )
                self.reporter.log_critic_check(check_rel, is_success, reason, token_usage=usage)

                if is_success:
                    logger.info(f"   ✅ 校验通过: {reason}")
                else:
                    logger.warning(f"   ❌ 校验失败: {reason}")
                    need_healing = True # 校验失败，触发自愈

            # --- C. 自愈流程 (如果需要) ---
            if need_healing:
                logger.info("   🔄 进入自愈流程...")
                if self._heal_step(operator, step_key, step_desc):
                    logger.info("   ✨ 步骤已修复，继续执行后续步骤...")
                    # 自愈成功，视为本步骤通过，继续循环
                else:
                    logger.error("   ⛔ 自愈失败，回放终止。")
                    all_passed = False
                    break

        close_operator()
        report_path = self.reporter.generate_html_report()
        
        if all_passed:
            logger.info(f"\n🎉 流程结束！报告: {os.path.abspath(report_path)}")
        else:
            logger.error(f"\n⛔ 流程失败。报告: {os.path.abspath(report_path)}")

if __name__ == "__main__":
    # 这里填入你的 JSON 路径
    json_file = "./scenarios/scenario_13459764b52a742d36553d5af9efc6be.json"
    
    try:
        replayer = ReplayAgent(json_file)
        replayer.run()
    except Exception as e:
        logger.error(f"运行出错: {e}", exc_info=True)