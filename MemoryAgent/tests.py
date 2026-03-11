from subagent.scenario_manager import ScenarioManager 
from subagent.scenario_agent import select_Operation
import copy
import re

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


workspace = "Test-hub"
scenario_manager = ScenarioManager(workspace)

caozuo = scenario_manager.list_operation_summaries()
buzhou = "新建项目表单中，将项目名称填写为 ttttest"
# print(caozuo)

# res, token = select_Operation(buzhou, str(caozuo))
res = {'decision': 'reuse_modified', 'operation_id': 'op_0864cf44', 'confidence': 1.0, 'reason': 'text: aitest -> tttest'}

# dictres = json.loads(res)
# res = {'decision': 'reuse', 'operation_id': 'op_8ca420c9', 'confidence': 1.0, 'reason': 'op_8ca420c9 的描述与当前步骤完全一致，可直接复用'}
decision = res["decision"]
operation_id = res["operation_id"]
confidence = res["confidence"]
reason = res["reason"]

if decision == "reuse":
    print(f"复用操作记忆，{operation_id}，置信度：{confidence}")
    print(scenario_manager.get_operation_by_id(operation_id))
else:
    print(res)
    actions = scenario_manager.get_operation_by_id(operation_id)["actions"]
    ss = apply_text_modification(actions, res["reason"])
    print(ss)

# print(ss)