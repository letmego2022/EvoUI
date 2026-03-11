# critic_agent.py

import json
import re
from utils import analyze_local_image
from subagent.prompt import CRITIC_SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)

def verify_step_success(screenshot_path, current_step_desc, expected_result=None):
    """
    使用视觉大模型验收当前步骤。
    
    Args:
        screenshot_path: 截图路径
        current_step_desc: 当前执行的步骤描述 (e.g., "输入 'admin' 到用户名框")
        expected_result: (可选) 预期结果描述 (e.g., "输入框显示 'admin'")
        
    Returns:
        result_data (dict): {
            "success": bool,
            "error_type": str,
            "suggestion": str,
            "reason": str,
            "usage": dict
        }
    """
    
    # 如果没有提供显式的预期结果，让 AI 基于步骤描述自行推断
    if not expected_result:
        expected_result = "Action completed successfully and visible on screen."

    # 构造符合新 Prompt 要求的输入
    user_content = f"""
    === 📍 刚刚执行的操作步骤 ===
    {current_step_desc}
    
    === 🎯 预期结果 ===
    {expected_result}
    
    === 🖼️ 当前截图 ===
    （见附件图片）

    请根据图片，并严格按照判定规则，分析该步骤是否成功。
    """
    
    full_prompt = f"{CRITIC_SYSTEM_PROMPT}\n\n{user_content}"

    try:
        # 调用 LLM (假设 analyze_local_image 支持传入 prompt 和 图片)
        response, token_usage = analyze_local_image(screenshot_path, full_prompt)
        
        # --- JSON 清洗与提取逻辑 ---
        # 移除可能存在的 Markdown 代码块标记
        cleaned = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
        cleaned = re.sub(r'^```\s*', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'\s*```$', '', cleaned, flags=re.MULTILINE)
        
        # 尝试提取 JSON 对象
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        
        if match:
            data = json.loads(match.group(0))
            
            # 解析字段，设置默认值以防 LLM 漏字段
            result_str = data.get("result", "FAIL").upper()
            is_success = (result_str == "SUCCESS")
            
            return {
                "success": is_success,
                "result": result_str, # "SUCCESS" or "FAIL"
                "error_type": data.get("error_type", "UNKNOWN"),
                "suggestion": data.get("suggestion", "NONE"),
                "reason": data.get("reason", "No reason provided by AI"),
                "usage": token_usage
            }
        else:
            # JSON 解析失败兜底
            return {
                "success": False,
                "result": "FAIL",
                "error_type": "SYSTEM_ERROR",
                "suggestion": "RETRY_ONCE",
                "reason": f"Failed to parse AI response: {response[:100]}...",
                "usage": token_usage
            }

    except Exception as e:
        # 运行异常兜底
        return {
            "success": False,
            "result": "FAIL",
            "error_type": "SYSTEM_ERROR",
            "suggestion": "TERMINATE",
            "reason": f"Program Error: {str(e)}",
            "usage": None
        }