import json
import os

class ConfigManager:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.systems_list = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_system_selection_list(self):
        """阶段一：路由选择列表 (不变)"""
        return [{"id": s["id"], "name": s["name"], "desc": s.get("description")} for s in self.systems_list]

    def get_system_config(self, system_id):
        """获取原始配置 (给执行器用，包含真实值)"""
        for sys in self.systems_list:
            if sys.get("id") == system_id:
                return sys
        return None

    def get_system_prompt_context(self, system_id):
        """
        【新增】阶段二专用：为 AI 生成脱敏的、带有参数指引的上下文描述
        """
        sys = self.get_system_config(system_id)
        if not sys:
            return None, None

        # 1. 提取基础信息
        target_url = sys.get("url")
        
        # 2. 构建描述文本
        context_lines = []
        context_lines.append(f"系统名称: {sys.get('name')}")
        context_lines.append(f"任务描述: {sys.get('description')}")
        context_lines.append(f"登录类型: {sys.get('auth_type')}")
        if sys.get('note'):
            context_lines.append(f"说明: {sys.get('note')}")
        

        # 3. 处理登录参数 (转化为 <tag>)
        if sys.get("auth_type") == "standard_login":
            context_lines.append("【登录参数】: 请使用 <username> 和 <password>")
        elif sys.get("auth_type") == "custom_function":
            context_lines.append(f"【登录方式】: 内置函数，请生成步骤说明调用 {sys.get('login_func')}，不需要输入密码")
        elif sys.get("auth_type") == "dynamic_url":
            context_lines.append(f"【链接获取方式】: 动态生成，请在 target_url 字段中填入:CALL:{sys.get('url_generator')}")

        # 4. 处理业务数据 (转化为 <tag>)
        b_data = sys.get("business_data", {})
        if b_data:
            # 提取所有 key 并加上尖括号，例如 ['<first_name>', '<zip>']
            tags = [f"<{k}>" for k in b_data.keys()]
            context_lines.append(f"【可用业务参数】: {', '.join(tags)}")

        return target_url, "\n".join(context_lines)