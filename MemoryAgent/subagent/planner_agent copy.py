import sys
import os
# ========================================================
# 核心修改：动态添加上级目录到系统路径
# ========================================================
# 1. 获取当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 2. 获取上级目录 (假设 utils.py 和 config.json 都在这一层)
parent_dir = os.path.dirname(current_dir)
# 3. 将上级目录加入 sys.path，这样 Python 才能找到那里的文件
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
import json
import re
import datetime
from utils import chat_mode_kimi
from tools.config_manager import ConfigManager

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
        print(f"JSON Parse Error: {e}\nRaw Text: {text}")
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
    print("🔍 [1/2] 正在匹配目标系统...")
    
    resp, usage = chat_mode_kimi(messages, stream=False)
    result = _parse_json_response(resp)
    
    return result.get("target_id"), usage

# --------------------------------------------------------------------------
# 第二步：生成执行计划 (Planner)
# --------------------------------------------------------------------------
def generate_execution_plan(system_id, user_query):
    # 1. 获取完整配置 (包含 URL, 账号, 占位符密码)
    sys_config = config_manager.get_system_config(system_id)
    
    if not sys_config:
        print(f"Error: System ID {system_id} not found in config.")
        return None, 0
    
    # 2. 核心 Prompt 设计
    planner_prompt = f"""
    你是一个精通 UI 自动化的 Planner Agent。你的任务是将用户指令转化为具体的浏览器操作步骤列表。
    
    === 当前任务环境 ===
    时间: {get_current_time()}
    系统名称: {sys_config.get('name')}
    系统配置数据: 
    {json.dumps(sys_config, indent=2, ensure_ascii=False)}
    
    === 规划规则 (必读) ===
    1. **数据引用原则**：
       - 如果需要登录，请直接使用配置中 `credentials` 下的 `username` 和 `password` 值。
       - **注意**：配置中的 password 可能是 "{{env:...}}" 格式的字符串，请**原封不动**地将其作为 value 填入，不要修改它，执行器会处理。
       - 如果需要填写表单（如姓名、邮编），请优先使用 `business_data` 中的数据。
       
    2. **动作类型 (action)**：
       - `goto`: 打开 URL (Step 1 必须是这个)。
       - `input`: 输入文本 (需要 selector 和 value)。
       - `click`: 点击元素 (需要 selector)。
       - `call`: 调用内置函数 (仅当 auth_type 为 custom_function 时使用)。
       
    3. **选择器 (selector)**：
       - 请根据字段名的通用英文习惯推测 selector（例如用户名为 #user-name, #username, [name="user"] 等）。
       - 如果不确定，请生成语义化的 selector 描述，方便视觉模型后续修正。

    === 用户指令 ===
    "{user_query}"
    
    === 输出要求 ===
    请直接返回一个 JSON List。示例结构：
    [
      {{"step": 1, "action": "goto", "url": "..."}},
      {{"step": 2, "action": "input", "selector": "#username", "value": "..."}},
      {{"step": 3, "action": "input", "selector": "#password", "value": "..."}},
      {{"step": 4, "action": "click", "selector": "#login-btn"}}
    ]
    """
    
    messages = [{"role": "user", "content": planner_prompt}]
    print(f"🧠 [2/2] 正在为 {sys_config.get('name')} 生成执行计划...")
    
    resp, usage = chat_mode_kimi(messages, stream=False)
    plan = _parse_json_response(resp)
    
    return plan, usage

# --------------------------------------------------------------------------
# 主流程入口
# --------------------------------------------------------------------------
def get_kimi_plan(user_query):
    total_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    
    # Step 1: 路由
    target_id, usage1 = select_system(user_query)
    if usage1: # 简单的 token 统计逻辑
        total_tokens['total_tokens'] += usage1.get('total_tokens', 0)
        
    if not target_id:
        print("❌ 未找到匹配的系统，无法生成计划。")
        return None, total_tokens
        
    # Step 2: 规划
    plan, usage2 = generate_execution_plan(target_id, user_query)
    if usage2:
        total_tokens['total_tokens'] += usage2.get('total_tokens', 0)
        
    return plan, total_tokens

# 测试用例
if __name__ == "__main__":
    # 模拟用户提问
    query = "登录 Swag Labs，然后帮我买个东西结账，姓名为 Liu"
    
    final_plan, tokens = get_kimi_plan(query)
    
    print("\n====== 最终生成的执行计划 ======")
    print(json.dumps(final_plan, indent=2, ensure_ascii=False))