import os
import time
import logging
from subagent.planner_agent import get_kimi_plan            
from global_operator import start_browser, get_operator, close_operator 
from utils import analyze_local_image, parse_json_safely, apply_text_modification           
from subagent.prompt import ui_auto_prompt                  
from subagent.report_manager import ReportManager   
from tools.auth_scripts import URL_GENERATORS       
from subagent.critic_agent import verify_step_success
from subagent.scenario_manager import ScenarioManager 
from subagent.scenario_agent import select_Operation
from tools.config_manager import ConfigManager

# --- 初始化配置 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
config_manager = ConfigManager(CONFIG_PATH)

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [%(levelname)s] - %(filename)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 全局常量
MAX_VISION_RETRIES = 5
reporter = ReportManager()
scenario_manager = None 

def execute_visual_step(operator, step_description, step_index, total_steps, global_context, op_id=None):
    """
    【闭环执行逻辑】：
    Executor 执行 -> Critic 验收 -> (失败则修正指令并重试)
    """
    logger.info(f"🔵 === 开始执行第 {step_index}/{total_steps} 步: {step_description} ===")
    reporter.log_step_start(step_index, total_steps, step_description)

    current_retry_count = 0
    current_step_instruction = step_description

    # =========================
    # 主 retry 循环
    # =========================
    while current_retry_count < MAX_VISION_RETRIES:
        current_retry_count += 1
        #  重要的获取SOM 的函数
        current_element_map = operator.extract_som()
                
        logger.info(
            f"   👁️ [第 {current_retry_count}/{MAX_VISION_RETRIES} 次尝试] 指令: {current_step_instruction}"
        )

        # 1️⃣ 截图
        abs_shot_path, rel_shot_path = reporter.get_new_screenshot_path(
            tag=f"s{step_index}_exec_{current_retry_count}"
        )
        try:
            operator.screenshot(abs_shot_path)
        except Exception as e:
            reporter.log_error(f"Screenshot failed: {e}")
            return False

        # 2️⃣ Executor Prompt
        full_prompt = (
            f"{ui_auto_prompt}\n\n"
            f"========================================\n"
            f"【🌍 全局上下文】\n{global_context}\n"
            f"【📍 当前目标】\n{current_step_instruction}\n"
            f"========================================\n\n"
            f"【操作说明】\n"
            f"1. 若已完成目标，返回 {{\"status\":\"completed\",\"reason\":\"...\"}}\n"
            f"2. 若系统错误，返回 {{\"status\":\"error\",\"reason\":\"...\"}}\n"
            f"3. 否则返回动作 JSON 列表\n"
        )

        # 3️⃣ 调用 Vision Executor
        try:
            ai_response, exec_usage = analyze_local_image(abs_shot_path, full_prompt)
            actions = parse_json_safely(ai_response)
        except Exception as e:
            reporter.log_error(f"Vision API error: {e}")
            continue

        reporter.log_vision_attempt(
            current_retry_count, rel_shot_path, full_prompt, ai_response, actions,
            token_usage=exec_usage
        )

        # =========================
        # 分支 A：解析失败
        # =========================
        if actions is None:
            logger.warning("⚠️ JSON parse failed")
            time.sleep(1.0)
            continue

        # =========================
        # 分支 B：Executor 认为已完成
        # =========================
        if isinstance(actions, dict):
            status = actions.get("status")

            if status == "completed":
                check_path, check_rel = reporter.get_new_screenshot_path(
                    tag=f"s{step_index}_check_final_{current_retry_count}"
                )
                operator.screenshot(check_path)

                check = verify_step_success(
                    screenshot_path=check_path,
                    current_step_desc=current_step_instruction,
                )

                reporter.log_critic_check(
                    check_rel, check["success"], check["reason"],
                    token_usage=check["usage"]
                )

                if check["success"]:
                    operator.clear_marker()
                    return True

                # ❌ Critic reject
                logger.warning(f"❌ check未通过: {check['reason']}")
                if check["suggestion"] == "TERMINATE":
                    return False

                if check["suggestion"] == "CLEAR_AND_RETYPE":
                    current_step_instruction = f"[Clear input first] {step_description}"
                elif check["suggestion"] == "RETRY_WITH_OFFSET":
                    current_step_instruction = f"[Click edge/icon] {step_description}"

                continue

            if status == "error":
                logger.error(actions.get("reason"))
                return False

        # =========================
        # 分支 C：Executor 给出动作
        # =========================
        if isinstance(actions, list):
            executed_actions = []
            action_executed = False

            for act in actions:
                try:
                    operator.execute_action(act, som_list=current_element_map)
                    executed_actions.append(act)
                    action_executed = True

                except Exception as e:
                    logger.warning(f"Action failed: {e}")

            if not action_executed:
                time.sleep(1.0)
                continue

            time.sleep(0.5)

            check_path, check_rel = reporter.get_new_screenshot_path(
                tag=f"s{step_index}_check_action_{current_retry_count}"
            )
            operator.screenshot(check_path)

            check = verify_step_success(
                screenshot_path=check_path,
                current_step_desc=current_step_instruction,
            )

            reporter.log_critic_check(
                check_rel, check["success"], check["reason"],
                token_usage=check["usage"]
            )

            if check["success"]:
                if scenario_manager:
                    scenario_manager.upsert_operation(
                        step_description, executed_actions, check["reason"], op_id=op_id
                    )
                operator.clear_marker()
                return True

            # ❌ Critic reject
            logger.warning(f"❌ Critic reject: {check['reason']}")

            if check["suggestion"] == "TERMINATE":
                return False

            if check["suggestion"] == "CLEAR_AND_RETYPE":
                current_step_instruction = f"先清空输入框，再输入：{step_description}"
            elif check["suggestion"] == "RETRY_WITH_OFFSET":
                current_step_instruction = f"点击边缘区域：{step_description}"

            continue

    reporter.log_error(
        f"Step {step_index} timed out after {MAX_VISION_RETRIES} retries"
    )
    return False


def execute_step_with_memory(operator, step_description, step_index, total_steps, global_context, actions=None):
    """
    【闭环执行逻辑】：
    记忆执行 执行 -> Critic 验收 -> (失败则返回视觉执行)
    """
    logger.info(f"🔵 === 记忆执行第 {step_index}/{total_steps} 步: {step_description} ===")
    reporter.log_step_start(step_index, total_steps, step_description)

    current_step_instruction = step_description
    #  重要的获取SOM 的函数
    current_element_map = operator.extract_som()
                
    # 1️⃣ 截图
    abs_shot_path, rel_shot_path = reporter.get_new_screenshot_path(
            tag=f"s{step_index}_exec_memory"
        )
    try:
        operator.screenshot(abs_shot_path)
    except Exception as e:
        reporter.log_error(f"Screenshot failed: {e}")
        return False
    reporter.log_vision_attempt(
            1, rel_shot_path, "记忆驱动", "记忆驱动", actions,
            token_usage=0
        )

    # =========================
    # 分支 A：解析失败
    # =========================
    if actions is None:
            logger.warning("⚠️ JSON parse failed")
            time.sleep(1.0)
            return False

    # =========================
    # 分支 B：Executor 给出动作 根据记忆执行
    # =========================
    if isinstance(actions, list):
        executed_actions = []
        action_executed = False

        for act in actions:
            try:
                operator.execute_action(act, som_list=current_element_map)
                executed_actions.append(act)
                action_executed = True

            except Exception as e:
                logger.warning(f"Action failed: {e}")

        if not action_executed:
            time.sleep(1.0)

        time.sleep(0.5)

        check_path, check_rel = reporter.get_new_screenshot_path(
                tag=f"s{step_index}_check_action_mer"
            )
        operator.screenshot(check_path)

        check = verify_step_success(
                screenshot_path=check_path,
                current_step_desc=current_step_instruction,
            )

        reporter.log_critic_check(
                check_rel, check["success"], check["reason"],
                token_usage=check["usage"]
            )

        if check["success"]:
                operator.clear_marker()
                return True
    return False

def resolve_real_url(plan_url):
    """
    解析动态 URL
    """
    if plan_url and isinstance(plan_url, str) and plan_url.startswith("CALL:"):
        func_name = plan_url.split("CALL:")[1].strip()
        logger.info(f"⚡ Resolving Dynamic URL: {func_name}")
        
        if func_name in URL_GENERATORS:
            try:
                real_url = URL_GENERATORS[func_name]()
                logger.info(f"✅ URL: {real_url}")
                return real_url
            except Exception as e:
                logger.error(f"❌ Function error: {e}")
                return None
        else:
            logger.error(f"❌ Unknown generator: {func_name}")
            return None
    return plan_url

def main(user_query):
    global scenario_manager
    reporter.set_task(user_query)
    logger.info(f"🚀 Launching Agent: {user_query}")

    try:
        # Phase 1: Planner
        logger.info("🧠 Planning Task...")
        result_data = get_kimi_plan(user_query)
        
        if not result_data or not result_data[0]:
            logger.error("❌ Planner returned empty.")
            return
        
        plan, planner_usage, target_id = result_data
        reporter.log_planner(user_query, plan, token_usage=planner_usage)
        
        raw_url = plan.get("target_url")
        steps = plan.get("steps", [])
        
        target_url = resolve_real_url(raw_url)
        if not target_url:
            logger.error("❌ Invalid Target URL")
            return
        # 获取系统凭证
        system_config = config_manager.get_system_config(target_id)
        if not system_config:
            logger.error(f"❌ No config found for ID: {target_id}")
            return
            
        logger.info(f"✅ Target System Workspace: {system_config.get('name')} (ID: {target_id})")
        logger.info(f"📝 Total Steps: {len(steps)}")
        # 这里是workspace
        scenario_manager = ScenarioManager(system_config.get('name'))
        plan['target_url'] = target_url # 更新 plan 用于记录
        if scenario_manager:
            scenario_manager.update_target_url(target_url)
        # Phase 2: Start Browser
        logger.info(f"🌐 Opening Browser: {target_url}")
        success, msg = start_browser(target_url, config_data=system_config)
        if not success:
            logger.error(f"❌ Browser Error: {msg}")
            return
            
        operator = get_operator()
        time.sleep(2)

        # Phase 3: Execute Loop
        all_steps_success = True
        
        for idx, step_desc in enumerate(steps):
            # 调用 AI 选择操作记忆
            res, token = select_Operation(user_query,step_desc, str(scenario_manager.list_operation_summaries()))
            step_icon = "🔹"
            logger.info(f"{step_icon} Step {idx+1}: {step_desc}")
            # -------------------------
            # 判断是否复用记忆
            # -------------------------
            if res["decision"] in ["reuse", "reuse_modified"]:
                logger.info(f"复用操作记忆: {res['operation_id']}，置信度: {res['confidence']}")
                # confidence = res["confidence"]
                # logger.info(f"当前置信度：{confidence}")  置信度 暂时 先不考虑
                
                # 获取原始操作
                original_op = scenario_manager.get_operation_by_id(res["operation_id"])
                
                # 如果是 reuse_modified，则替换 text 参数
                actions_to_execute = original_op["actions"]
                if res["decision"] == "reuse_modified":
                    logger.info("需要调整写入参数...,进行参数替换")
                    actions_to_execute = apply_text_modification(actions_to_execute, res["reason"])
                
                # -------------------------
                # 执行步骤（带 memory 的执行器）
                # -------------------------
                step_success = execute_step_with_memory(
                    operator=operator,
                    step_description=step_desc,
                    step_index=idx + 1,
                    total_steps=len(steps),
                    global_context=user_query,
                    actions=actions_to_execute
                )
                
                # -------------------------
                # 检查失败则转交视觉执行
                # -------------------------
                if not step_success:
                    logger.warning(f"⛔ 转交视觉执行 Step {idx+1}")
                    print(f"执行没成功！发送了operationid:{res['operation_id']}")
                    step_success = execute_visual_step(
                        operator=operator,
                        step_description=step_desc,
                        step_index=idx + 1,
                        total_steps=len(steps),
                        global_context=user_query,
                        op_id=res["operation_id"]
                    )
                    
            else:
                # 没有匹配到操作记忆
                logger.info("没有匹配到操作记忆，执行视觉执行")
                step_success = execute_visual_step(
                    operator=operator,
                    step_description=step_desc,
                    step_index=idx + 1,
                    total_steps=len(steps),
                    global_context=user_query
                )

            # -------------------------
            # 全局任务失败处理
            # -------------------------
            if not step_success:
                logger.error(f"⛔ Task Aborted at Step {idx+1}")
                all_steps_success = False
                break
            
            time.sleep(1)  # Step 间隔

        # Final Result
        if all_steps_success:
            logger.info("🎉 Mission Complete!")
            reporter.log_success("Mission Complete")
        else:
            logger.warning("⚠️ Mission Failed")
            reporter.log_error("Mission Failed")

    except KeyboardInterrupt:
        logger.info("🛑 User Interrupted")
    except Exception as e:
        logger.error(f"Global Exception: {e}", exc_info=True)
        reporter.log_error(f"Global Exception: {e}")
    finally:
        close_operator()
        report_path = reporter.generate_html_report()
        logger.info(f"📄 Report generated: {os.path.abspath(report_path)}")

if __name__ == "__main__":
        # 定义测试任务
    # user_query = "在 Swag Labs 购买一个背包，并最后checkout"
    user_query = "在 test-hub 中 添加一个project:aitest4"
    # user_query = "在 test-hub中 给项目aitest3 添加一个Module【模块】:testmodel2"
    # user_query = "在 test-hub中 在项目aitest3 下的 Module:testmodel2 中 添加一个userstory 你帮我想一个关于登录的吧 title是login 内容你构造一个"
    # user_query = "在 test-hub中 进入AI agents管理，把 batest 删除掉"
    # user_query = "在 test-hub 中 把项目 aitest4 删除掉"
    main(user_query)