from openai import OpenAI
# from zhipuai import ZhipuAI
from config import ZHIPU_API_KEY,ZHIPU_MODEL_NAME
from config import API_KEY,BASE_URL,API_MODEL
import io
import contextlib
import os
import time
import hashlib
import base64
import mimetypes
import re
import json
import re
import ast
import logging
import json, ast, re, logging
import copy
import re
from zai import ZhipuAiClient

logger = logging.getLogger(__name__)

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
def generate_screenshot_name(task_desc, suffix=""):
    safe_name = hashlib.md5(task_desc.encode()).hexdigest()[:8]
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_name}_{timestamp}{suffix}.png"
    return os.path.join("static/screenshots", filename)

def apply_text_modification(actions, reason):
    """
    根据 reason 替换 actions 中的 text
    reason 示例： "text: aitest -> tttest"
    
    :param actions: 原始 actions 列表（List[Dict]）
    :param reason: AI 输出的 reason 字符串
    :return: 修改后的 actions 列表
    """
    modified_actions = copy.deepcopy(actions)

    # 使用正则解析 reason 中的 text 差异
    match = re.search(r"text:\s*(\S+)\s*->\s*(\S+)", reason)
    if match:
        old_text, new_text = match.groups()
        for act in modified_actions:
            if act.get("text") == old_text:
                act["text"] = new_text

    return modified_actions

def ensure_dir(path="screenshots"):
    if not os.path.exists(path):
        os.makedirs(path)

def task_is_finished(latest_step_json):
    # 可扩展：AI 返回特定标记、或特定 UI 元素出现等
    return False

def run_python_code(code: str):
    output = io.StringIO()
    local_vars = {}

    with contextlib.redirect_stdout(output):
        try:
            # 尝试先作为表达式执行
            result = eval(code, {}, local_vars)
        except SyntaxError:
            # 如果不是表达式，是代码块，就用 exec 执行
            exec(code, {}, local_vars)
            result = None
        except Exception as e:
            result = f"❌ 错误: {e}"

    printed_output = output.getvalue()
    return printed_output.strip() or result

def chat_mode_kimi(messages, stream=False):
    if stream:
        def generator():
            completion = client.chat.completions.create(
                model=API_MODEL,
                messages=messages,
                temperature=0.3,
                stream=True
            )
            collected_messages = []
            for chunk in completion:
                chunk_message = chunk.choices[0].delta.content
                if not chunk_message:
                    continue
                collected_messages.append(chunk_message)
                yield chunk_message

            result = ''.join(collected_messages)
            if '</think>' in result:
                result = result.split('</think>', 1)[1].strip()
            result_holder["text"] = result  # 将最终结果写入外部变量

        result_holder = {"text": ""}
        return generator(), result_holder
    else:
        completion = client.chat.completions.create(
            model=API_MODEL,
            messages=messages,
            temperature=0.3
        )
        result = completion.choices[0].message.content
        
        # 处理思考标签
        if '</think>' in result:
            result = result.split('</think>', 1)[1].strip()
            
        # 【新增】获取 Token 消耗
        token_usage = completion.usage
        
        # 【修改】返回元组 (文本, usage对象)
        return result, token_usage

def chat_mode_zhipu(messages):
    """
    基础调用函数
    Returns:
        tuple: (content_string, usage_object)
    """
    try:
        client = ZhipuAiClient(api_key=ZHIPU_API_KEY)
        response = client.chat.completions.create(
            model=ZHIPU_MODEL_NAME, 
            messages=messages
        )
        # 1. 提取回复文本
        content = response.choices[0].message.content.strip()
        # 2. 【核心修改】提取 Token 消耗信息
        # response.usage 通常包含 prompt_tokens, completion_tokens, total_tokens
        token_usage = response.usage 
        return content, token_usage
        
    except Exception as e:
        print(f"Error calling ZhipuAI API: {e}")
        # 向上层抛出异常，让API路由统一处理错误响应
        raise

def analyze_local_image(image_path, prompt_text="这张图里有什么？"):
    """
    封装函数：将本地图片转换为 Base64 并调用智谱视觉模型。
    
    Returns:
        tuple: (ai_response_text, token_usage_object)
    """
    
    # 1. 检查文件是否存在
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件未找到: {image_path}")
    
    # 2. 自动判断图片类型 (jpg, png, etc.) 用于构造 data URI
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "image/jpeg" # 默认 fallback
        
    # 3. 读取并进行 Base64 编码
    try:
        with open(image_path, "rb") as image_file:
            base64_data = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        raise Exception(f"读取或编码图片失败: {e}")

    # 4. 构造智谱 API 要求的数据格式
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": prompt_text
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_data}"
                    }
                }
            ]
        }
    ]
    
    # 5. 调用基础函数，获取返回值（文本 + usage）
    content, usage = chat_mode_zhipu(messages)

    # 6. 返回元组
    return content, usage

def parse_json_safely(text):
    """
    超强容错 JSON 解析
    保证返回：
      - List[Dict]（普通动作）
      - Dict（特殊 status: completed / error）
      - 解析失败返回 None
    """
    if not text or not isinstance(text, str):
        return None

    # 1️⃣ 去除 Markdown 代码块
    cleaned_text = re.sub(r'```json\s*', '', text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'```\s*', '', cleaned_text)
    cleaned_text = cleaned_text.strip()

    try:
        # 2️⃣ 提取最外层 JSON 片段
        start_idx, end_idx = -1, -1
        for i, ch in enumerate(cleaned_text):
            if ch in ('{', '['):
                start_idx = i
                break
        for i, ch in enumerate(reversed(cleaned_text)):
            if ch in ('}', ']'):
                end_idx = len(cleaned_text) - i
                break
        if start_idx == -1 or end_idx == -1:
            raise ValueError("找不到 JSON 起止符")

        candidate = cleaned_text[start_idx:end_idx]

        parsed = None
        # 3️⃣ 标准 JSON
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            pass

        # 4️⃣ Python literal（容忍单引号）
        if parsed is None:
            try:
                parsed = ast.literal_eval(candidate)
            except Exception:
                pass

        if parsed is None:
            raise ValueError("JSON / literal_eval 均失败")

        # 5️⃣ 核心增强：处理特殊 dict
        if isinstance(parsed, dict):
            status = parsed.get("status")
            if status in ("completed", "error"):
                return parsed      # 保留原样 dict
            else:
                return [parsed]    # 普通 dict 包成 list

        if isinstance(parsed, list):
            return parsed

        logger.error(f"⚠️ 解析结果不是 dict / list，而是 {type(parsed)}")
        return None

    except Exception as e:
        logger.error(f"❌ JSON 解析失败: {e}")
        logger.error(f"原始文本:\n{text}\n----------------")
        return None

