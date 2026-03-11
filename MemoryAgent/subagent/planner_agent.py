# planner_agent.py
import json
import re
import os
from utils import chat_mode_kimi # 导入你的函数
import json
import re
import datetime
from tools.config_manager import ConfigManager
from subagent.prompt import PLANNER_SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)

# 初始化
config_manager = ConfigManager("config.json")

def _parse_json_response(text):
    """
    清洗并解析 LLM 返回的 JSON
    """
    try:
        # 移除 markdown 代码块
        cleaned = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        cleaned = re.sub(r'^```\s*', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'\s*```$', '', cleaned, flags=re.MULTILINE)
        # 尝试提取 [] 或 {}
        match = re.search(r'(\[.*\]|\{.*\})', cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(cleaned)
    except Exception as e:
        logger.warning(f"JSON Parse Error: {e}\nRaw Text: {text}")
        return None

def get_current_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M")

# --------------------------------------------------------------------------
# 第一步：系统路由 (Router)
# --------------------------------------------------------------------------
def select_system(user_query):
    # 1. 获取精简列表
    candidates = config_manager.get_system_selection_list()
    
    router_prompt = f"""
    你是一个任务分发助手。请根据用户指令，从下方可选系统中选择最匹配的一个。
    
    【可选系统列表】:
    {json.dumps(candidates, indent=2, ensure_ascii=False)}
    
    【用户指令】: "{user_query}"
    
    【要求】:
    - 如果匹配成功，返回系统的 "id"。
    - 如果没有匹配的系统，返回 null。
    - 仅返回 JSON 格式: {{"target_id": "string_or_null", "reason": "string"}}
    """
    
    messages = [{"role": "user", "content": router_prompt}]
    logger.info("🔍 [1/2] 正在匹配目标系统...")
    
    resp, usage = chat_mode_kimi(messages, stream=False)
    result = _parse_json_response(resp)
    
    return result.get("target_id"), usage

# --------------------------------------------------------------------------
# 第二步：生成执行计划 (Planner)
# --------------------------------------------------------------------------
def generate_execution_plan(system_id, user_query):
    target_url, context_text = config_manager.get_system_prompt_context(system_id)
    
    if not target_url:
        logger.warning(f"Error: System {system_id} not found.")
        return None

    # 2. 组装 Prompt
    user_context = f"""
    === 当前时间 ===
    {get_current_time()}
    
    === 系统上下文 (包含可用参数) ===
    {context_text}
    
    === 系统入口 URL ===
    {target_url}
    
    === 用户指令 ===
    {user_query}
    """
    
    messages = [
        {"role": "system", "content": PLANNER_SYSTEM_PROMPT}, # 使用上面定义的新Prompt
        {"role": "user", "content": user_context}
    ]
    
    logger.info(f"🧠 [Planner] 正在生成带有占位符的视觉计划...")

    # 【修改】接收两个返回值
    response_text, token_usage = chat_mode_kimi(messages, stream=False)

    # JSON 清洗与解析
    try:
        # 1. 移除 Markdown 代码块标记
        cleaned_text = re.sub(r'^```json\s*', '', response_text, flags=re.MULTILINE)
        cleaned_text = re.sub(r'^```\s*', '', cleaned_text, flags=re.MULTILINE)
        cleaned_text = re.sub(r'\s*```$', '', cleaned_text, flags=re.MULTILINE)
        
        # 2. 提取 JSON 对象 (防止前后有废话)
        match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
        if match:
            cleaned_text = match.group(0)
            
        plan_json = json.loads(cleaned_text)
         # 【修改】返回元组：(计划JSON, Token消耗)
        return plan_json, token_usage
        
    except json.JSONDecodeError:
        logger.error(f"❌ JSON 解析失败，原文内容:\n{response_text}")
        return None
    
    


# --------------------------------------------------------------------------
# 主流程入口
# --------------------------------------------------------------------------
def get_kimi_plan(user_query):
    total_tokens = 0
    
    # Step 1: 路由
    target_id, usage1 = select_system(user_query)
        
    if not target_id:
        logger.warning("❌ 未找到匹配的系统，无法生成计划。")

    # Step 2: 规划
    plan, usage2 = generate_execution_plan(target_id, user_query)
        
    return plan, total_tokens, target_id