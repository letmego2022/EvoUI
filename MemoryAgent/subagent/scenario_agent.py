# scenario_agent.py
import json
import re
from utils import chat_mode_kimi # 导入你的函数
import logging

logger = logging.getLogger(__name__)

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
        logger.error(f"JSON Parse Error: {e}\nRaw Text: {text}")
        return None

# --------------------------------------------------------------------------
# 第一步：系统路由 (Router)
# --------------------------------------------------------------------------
def select_Operation(mubiao, Current_steps, Available_Operations):
    # 1. 获取精简列表
    
    prompt = f"""
你是一个 UI 自动化 Agent，需要从已有操作中选择最合适的一步来完成当前步骤。
【选择原则（必须同时满足）】
1. 所选 Operation 必须同时符合：
   - 当前步骤目标（Step Goal）
   - 整体流程目标（Global Goal）
2. 如果某个 Operation 的行为相似，但其历史语义或使用场景
   与当前整体目标不一致，则禁止选择。

【整体流程目标】
{mubiao}

【当前操作步骤】
{Current_steps}

【可用操作（仅摘要）】
{Available_Operations}

【任务】
判断是否有“已有操作”可以复用来完成当前步骤，并给出合理的置信度。

【复用判定标准】
- 仅当【动作类型 + 执行顺序 + 目标元素语义】一致时，才允许复用
- 如果仅输入参数不同（如 text 不同），返回 decision = "reuse_modified"
  - 在 reason 中必须使用固定格式标记参数差异，例如：
    "text: old_value -> new_value"
- 如果目标元素绑定特定业务模块、弹窗或页面上下文不同，则应降低置信度
- 如果操作强依赖坐标位置（即使 action 相同），也必须降低置信度
- 动作类型、顺序或目标语义不同，则 decision = "new"
- 无法判断时可返回 "unsure"

【置信度评估规则（必须考虑）】
请综合以下因素评估 confidence（0~1）：
1. 操作是否为通用 UI 行为（如输入框输入、通用保存按钮）
2. 是否仅参数不同，而非结构不同
3. 是否绑定特定模块、弹窗或业务上下文
4. 是否对坐标位置高度敏感

【规则】
1. 只能从给定的 operation id 中选择
2. 不允许猜测不存在的 id
3. 必须严格返回 JSON，不要任何额外文本

【返回格式】
{{
  "decision": "reuse | reuse_modified | new | unsure",
  "operation_id": "operation id 或 null",
  "confidence": 0.0,
  "reason": "简要说明判断依据"
}}
"""
    messages = [{"role": "user", "content": prompt}]
    logger.info("🔍 [**] 正在匹配操作记忆...")
    
    resp, usage = chat_mode_kimi(messages, stream=False)
    result = _parse_json_response(resp)
    
    return result, usage
