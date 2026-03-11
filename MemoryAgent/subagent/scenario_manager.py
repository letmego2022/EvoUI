import os
import json
import time
import uuid
import logging

class ScenarioManager:
    def __init__(self, workspace, base_dir="scenarios"):
        self.logger = logging.getLogger("ScenarioManager")
        self.base_dir = base_dir
        self.filepath = os.path.join(base_dir, f"{workspace}.json")

        self.data = {
            "workspace": workspace,
            "target_url": "",
            "updated_at": "",
            "operations": {}
        }

        self._load()

    # ---------- 基础工具 ----------

    def _now(self):
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                self.logger.info("📂 已加载已有 operations")
            except Exception as e:
                self.logger.error(f"加载失败: {e}")

    def _flush(self):
        self.data["updated_at"] = self._now()
        os.makedirs(self.base_dir, exist_ok=True)
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            self.logger.info("💾 operations 已保存")
        except Exception as e:
            self.logger.error(f"保存失败: {e}")

    # ---------- 公共 API ----------

    def update_target_url(self, url):
        self.data["target_url"] = url
        self._flush()

    def get_operations(self):
        """读取所有已保存的 operations"""
        return self.data.get("operations", {})
    
    def list_operation_summaries(self):
        """
        返回轻量 operation 列表，用于 AI 选择
        """
        summaries = []
        for op_id, op in self.data.get("operations", {}).items():
            summaries.append({
                "id": op_id,
                "description": op.get("description", "")
            })
        return summaries
    
    def get_operation_by_id(self, op_id):
        """
        根据 operation_id 获取完整 operation 定义
        """
        return self.data.get("operations", {}).get(op_id)

    def upsert_operation(self, description, actions, assertion, op_id=None):
        """
        新增 or 更新一个 operation

        规则：
        - 只有 1 个 action → description 强制使用 action.description
        - 多个 action → 使用外部传入的 description
        """

        if not actions or not isinstance(actions, list):
            raise ValueError("actions must be a non-empty list")

        if not op_id:
            op_id = f"op_{uuid.uuid4().hex[:8]}"

        # ========= 核心规则在这里 =========
        if len(actions) == 1:
            action_desc = actions[0].get("description")
            if action_desc:
                description = action_desc
        # =================================

        ops = self.data["operations"]

        if op_id not in ops:
            # 新增
            ops[op_id] = {
                "description": description,
                "actions": actions,
                "assertion": assertion,
                "stats": {
                    "success": 0,
                    "fail": 0
                },
                "created_at": self._now(),
                "last_used": ""
            }
        else:
            # 更新
            ops[op_id]["description"] = description
            ops[op_id]["actions"] = actions
            ops[op_id]["assertion"] = assertion

        # ⚠️ 不在 upsert 阶段统计成功
        ops[op_id]["last_used"] = self._now()

        self._flush()
        return op_id


    def mark_operation_fail(self, op_id):
        """记录 operation 失败"""
        ops = self.data["operations"]
        if op_id in ops:
            ops[op_id]["stats"]["fail"] += 1
            self._flush()
