import os
import time
import json
from datetime import datetime

class ReportManager:
    def __init__(self, base_dir="test_reports"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_dir = os.path.join(base_dir, f"run_{timestamp}")
        self.screenshot_dir = os.path.join(self.report_dir, "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        self.logs = []
        self.start_time = time.time()
        self.task_description = ""
        
        # 【新增】Token 统计总数
        self.total_tokens = 0
        self.total_cost_estimate = 0.0 # 可选：估算金额

    def set_task(self, task):
        self.task_description = task

    def get_new_screenshot_path(self, tag="step"):
        filename = f"{tag}_{int(time.time()*1000)}.jpg"
        abs_path = os.path.join(self.screenshot_dir, filename)
        rel_path = f"./screenshots/{filename}"
        return abs_path, rel_path

    # 【修改】增加 token_usage 参数
    def log_planner(self, input_text, plan_json, token_usage=None):
        t_count = token_usage.total_tokens if token_usage else 0
        self.total_tokens += t_count
        
        self.logs.append({
            "type": "planner",
            "time": datetime.now().strftime("%H:%M:%S"),
            "input": input_text,
            "output": json.dumps(plan_json, indent=2, ensure_ascii=False),
            "tokens": t_count # 记录单次消耗
        })

    def log_step_start(self, step_idx, total, description):
        self.logs.append({
            "type": "step_start",
            "time": datetime.now().strftime("%H:%M:%S"),
            "title": f"Step {step_idx}/{total}: {description}"
        })

    # 【修改】增加 token_usage 参数
    def log_vision_attempt(self, retry_count, screenshot_rel_path, prompt, ai_response, action_json=None, token_usage=None):
        t_count = token_usage.total_tokens if token_usage else 0
        self.total_tokens += t_count

        self.logs.append({
            "type": "vision_attempt",
            "time": datetime.now().strftime("%H:%M:%S"),
            "retry": retry_count,
            "image": screenshot_rel_path,
            "prompt": prompt,
            "response": ai_response,
            "action": json.dumps(action_json, indent=2, ensure_ascii=False) if action_json else "Parse Error",
            "tokens": t_count # 记录单次消耗
        })

    # 【修改】增加 token_usage 参数
    def log_critic_check(self, screenshot_rel_path, is_success, reason, token_usage=None):
        t_count = token_usage.total_tokens if token_usage else 0
        self.total_tokens += t_count

        self.logs.append({
            "type": "critic_check",
            "time": datetime.now().strftime("%H:%M:%S"),
            "image": screenshot_rel_path,
            "success": is_success,
            "reason": reason,
            "tokens": t_count # 记录单次消耗
        })

    def log_success(self, msg):
        self.logs.append({"type": "success", "msg": msg, "time": datetime.now().strftime("%H:%M:%S")})

    def log_error(self, msg):
        self.logs.append({"type": "error", "msg": msg, "time": datetime.now().strftime("%H:%M:%S")})

    def generate_html_report(self):
        """生成最终 HTML 报告 (内嵌 SVG 图标版)"""
        duration = int(time.time() - self.start_time)
        
        # 1. 定义一个硬币的 SVG 图标 (黄色描边)
        COIN_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px; margin-bottom: 2px;"><path d="M10.101 4C8.181 4 6.375 4.3 5 4.818M13.899 20c1.92 0 3.726-.3 5.101-.818M4 19.182C4 20.187 7.582 21 12 21c4.418 0 8-.813 8-1.818V14.5c0 1.005-3.582 1.818-8 1.818-2.607 0-4.927-.284-6.429-.737M4 10.818C4 11.823 7.582 12.636 12 12.636c4.418 0 8-.813 8-1.818V8.136c0 1.005-3.582 1.818-8 1.818-2.607 0-4.927-.284-6.429-.737M4 8.136V4.818C4 3.813 7.582 3 12 3c4.418 0 8 .813 8 1.818v3.318"/></svg>"""

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI Agent Execution Report</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; margin: 0; padding: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #1a73e8; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                .meta {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
                
                .log-entry {{ margin-bottom: 20px; border-left: 4px solid #ddd; padding-left: 15px; }}
                .planner {{ border-left-color: #9c27b0; background: #fcf0ff; padding: 10px; border-radius: 4px; }}
                .step-start h3 {{ background: #e8f0fe; padding: 10px; border-radius: 5px; color: #1967d2; margin-top: 30px; }}
                .vision-attempt {{ display: flex; gap: 20px; margin-top: 15px; border-bottom: 1px dashed #eee; padding-bottom: 15px; }}
                .vision-left {{ flex: 1; min-width: 300px; }}
                .vision-right {{ flex: 2; }}
                
                .screenshot {{ width: 100%; border: 1px solid #ddd; border-radius: 5px; cursor: pointer; transition: transform 0.2s; }}
                .screenshot:hover {{ transform: scale(1.02); }}
                
                .prompt-box {{ background: #f8f9fa; padding: 8px; font-size: 0.85em; color: #555; border-radius: 4px; max-height: 100px; overflow-y: auto; }}
                .response-box {{ background: #e6fffa; padding: 10px; border-radius: 4px; border: 1px solid #b2f5ea; white-space: pre-wrap; font-family: monospace; }}
                
                .badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; color: white; font-weight: bold; }}
                .badge-retry {{ background: #f59e0b; }}
                .badge-critic {{ background: #6366f1; }}
                
                .token-tag {{ background: #fffcf5; color: #b45309; padding: 2px 8px; border-radius: 6px; font-size: 0.8em; margin-left: 8px; border: 1px solid #fcd34d; font-weight: 500; }}
                
                .success {{ color: #059669; font-weight: bold; padding: 10px; background: #d1fae5; border-radius: 5px; }}
                .error {{ color: #dc2626; font-weight: bold; padding: 10px; background: #fee2e2; border-radius: 5px; }}
                pre {{ margin: 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 AI Agent Execution Report</h1>
                <div class="meta">
                    <p><strong>Task:</strong> {self.task_description}</p>
                    <p>
                        <strong>Date:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | 
                        <strong>Duration:</strong> {duration}s |
                        <strong style="color:#d97706; margin-left:15px;">
                            {COIN_SVG} Total Tokens: {self.total_tokens}
                        </strong>
                    </p>
                </div>
                
                <div class="logs">
        """
        
        for log in self.logs:
            # 使用内嵌 SVG，不依赖外部 CSS
            token_val = log.get("tokens")
            if token_val is not None:
                token_html = f'<span class="token-tag" title="Token Usage">{COIN_SVG}{token_val}</span>'
            else:
                token_html = ""

            if log['type'] == 'planner':
                html_content += f"""
                <div class="log-entry planner">
                    <h4>🧠 Mission Planning {token_html}</h4>
                    <details>
                        <summary>View Plan Details</summary>
                        <pre>{log['output']}</pre>
                    </details>
                </div>
                """
            
            elif log['type'] == 'step_start':
                html_content += f"""
                <div class="log-entry step-start">
                    <h3>📍 {log['title']}</h3>
                </div>
                """
            
            elif log['type'] == 'vision_attempt':
                html_content += f"""
                <div class="vision-attempt">
                    <div class="vision-left">
                        <span class="badge badge-retry">Attempt #{log['retry']}</span>
                        {token_html}
                        <div style="margin-top:5px; font-size:0.8em; color:#888;">{log['time']}</div>
                        <a href="{log['image']}" target="_blank">
                            <img src="{log['image']}" class="screenshot" alt="screenshot">
                        </a>
                    </div>
                    <div class="vision-right">
                        <div><strong>Executor Thought:</strong></div>
                        <div class="response-box">{log['response']}</div>
                        
                        <div style="margin-top:10px;"><strong>🛠️ Parsed Actions:</strong></div>
                        <pre style="background:#333; color:#fff; padding:10px; border-radius:4px;">{log['action']}</pre>
                    </div>
                </div>
                """
            
            elif log['type'] == 'critic_check':
                status_class = "success" if log['success'] else "error"
                status_text = "✅ PASSED" if log['success'] else "❌ FAILED"
                border_color = "#059669" if log['success'] else "#dc2626"
                bg_color = "#f0fdf4" if log['success'] else "#fef2f2"
                
                html_content += f"""
                <div class="vision-attempt" style="border-left: 4px solid {border_color}; background: {bg_color};">
                    <div class="vision-left">
                        <span class="badge badge-critic">⚖️ Critic Review</span>
                        {token_html}
                        <div style="margin-top:5px; font-size:0.8em; color:#888;">{log['time']}</div>
                        <a href="{log['image']}" target="_blank">
                            <img src="{log['image']}" class="screenshot" alt="screenshot">
                        </a>
                    </div>
                    <div class="vision-right">
                        <div class="{status_class}">
                            {status_text}: {log['reason']}
                        </div>
                    </div>
                </div>
                """
            
            elif log['type'] == 'success':
                html_content += f'<div class="log-entry success">🎉 {log["msg"]}</div>'
            
            elif log['type'] == 'error':
                html_content += f'<div class="log-entry error">⛔ {log["msg"]}</div>'

        html_content += """
                </div>
            </div>
        </body>
        </html>
        """
        
        report_path = os.path.join(self.report_dir, "report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        return report_path

class ReportManagerPara:
    def __init__(self, task_id, base_dir="test_reports"):
        """
        初始化报告管理器
        :param task_id: 任务唯一标识，用于生成独立的文件名
        :param base_dir: 报告存放的根目录
        """
        self.task_id = str(task_id)  # 强转字符串，防止拼接报错
        self.start_time = time.time()
        
        # 1. 按照日期创建父文件夹，例如: test_reports/20231027
        # 这样一天的所有并行任务都在这一个文件夹里
        date_str = datetime.now().strftime("%Y%m%d")
        self.base_dir = os.path.join(base_dir, date_str)
        
        # 2. 创建公共截图文件夹: test_reports/20231027/screenshots
        self.screenshot_dir = os.path.join(self.base_dir, "screenshots")
        
        # exist_ok=True 是多进程安全的关键，防止多个进程同时创建文件夹报错
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        self.logs = []
        self.task_description = ""
        self.total_tokens = 0

    def set_task(self, task):
        self.task_description = task

    def get_new_screenshot_path(self, tag="step"):
        """
        生成截图路径。
        关键点：文件名必须包含 task_id，否则并行运行时不同任务的截图会互相覆盖。
        """
        # 文件名: task_1_s1_try1_169837482.jpg
        filename = f"task_{self.task_id}_{tag}_{int(time.time()*1000)}.jpg"
        
        # 1. 绝对路径：用于 Playwright 保存文件
        abs_path = os.path.join(self.screenshot_dir, filename)
        
        # 2. 相对路径：用于 HTML 引用
        # HTML文件在 base_dir，图片在 base_dir/screenshots
        rel_path = f"./screenshots/{filename}"
        
        return abs_path, rel_path

    # --- 日志记录方法 (保持逻辑不变) ---

    def log_planner(self, input_text, plan_json, token_usage=None):
        t_count = token_usage.total_tokens if token_usage else 0
        self.total_tokens += t_count
        self.logs.append({
            "type": "planner", 
            "time": datetime.now().strftime("%H:%M:%S"),
            "input": input_text, 
            "output": json.dumps(plan_json, indent=2, ensure_ascii=False),
            "tokens": t_count
        })

    def log_step_start(self, step_idx, total, description):
        self.logs.append({
            "type": "step_start", 
            "time": datetime.now().strftime("%H:%M:%S"),
            "title": f"Step {step_idx}/{total}: {description}"
        })

    def log_vision_attempt(self, retry_count, screenshot_rel_path, prompt, ai_response, action_json=None, token_usage=None):
        t_count = token_usage.total_tokens if token_usage else 0
        self.total_tokens += t_count
        self.logs.append({
            "type": "vision_attempt", 
            "time": datetime.now().strftime("%H:%M:%S"),
            "retry": retry_count, 
            "image": screenshot_rel_path,
            "prompt": prompt, 
            "response": ai_response,
            "action": json.dumps(action_json, indent=2, ensure_ascii=False) if action_json else "Parse Error",
            "tokens": t_count
        })

    def log_critic_check(self, screenshot_rel_path, is_success, reason, token_usage=None):
        t_count = token_usage.total_tokens if token_usage else 0
        self.total_tokens += t_count
        self.logs.append({
            "type": "critic_check", 
            "time": datetime.now().strftime("%H:%M:%S"),
            "image": screenshot_rel_path, 
            "success": is_success, 
            "reason": reason,
            "tokens": t_count
        })

    def log_success(self, msg):
        self.logs.append({"type": "success", "msg": msg, "time": datetime.now().strftime("%H:%M:%S")})

    def log_error(self, msg):
        self.logs.append({"type": "error", "msg": msg, "time": datetime.now().strftime("%H:%M:%S")})

    # --- HTML 生成方法 ---

    def generate_html_report(self):
        duration = int(time.time() - self.start_time)
        COIN_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px; margin-bottom: 2px;"><path d="M10.101 4C8.181 4 6.375 4.3 5 4.818M13.899 20c1.92 0 3.726-.3 5.101-.818M4 19.182C4 20.187 7.582 21 12 21c4.418 0 8-.813 8-1.818V14.5c0 1.005-3.582 1.818-8 1.818-2.607 0-4.927-.284-6.429-.737M4 10.818C4 11.823 7.582 12.636 12 12.636c4.418 0 8-.813 8-1.818V8.136c0 1.005-3.582 1.818-8 1.818-2.607 0-4.927-.284-6.429-.737M4 8.136V4.818C4 3.813 7.582 3 12 3c4.418 0 8 .813 8 1.818v3.318"/></svg>"""

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Task {self.task_id} Report</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background: #f0f2f5; margin: 0; padding: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #1a73e8; border-bottom: 2px solid #eee; padding-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }}
                .task-badge {{ background: #1a73e8; color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.5em; vertical-align: middle; }}
                .meta {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
                .log-entry {{ margin-bottom: 20px; border-left: 4px solid #ddd; padding-left: 15px; }}
                .planner {{ border-left-color: #9c27b0; background: #fcf0ff; padding: 10px; border-radius: 4px; }}
                .step-start h3 {{ background: #e8f0fe; padding: 10px; border-radius: 5px; color: #1967d2; margin-top: 30px; }}
                .vision-attempt {{ display: flex; gap: 20px; margin-top: 15px; border-bottom: 1px dashed #eee; padding-bottom: 15px; }}
                .vision-left {{ flex: 1; min-width: 300px; }}
                .vision-right {{ flex: 2; }}
                .screenshot {{ width: 100%; border: 1px solid #ddd; border-radius: 5px; cursor: pointer; transition: transform 0.2s; }}
                .screenshot:hover {{ transform: scale(1.02); }}
                .response-box {{ background: #e6fffa; padding: 10px; border-radius: 4px; border: 1px solid #b2f5ea; white-space: pre-wrap; font-family: monospace; }}
                .badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; color: white; font-weight: bold; }}
                .badge-retry {{ background: #f59e0b; }}
                .badge-critic {{ background: #6366f1; }}
                .token-tag {{ background: #fffcf5; color: #b45309; padding: 2px 8px; border-radius: 6px; font-size: 0.8em; margin-left: 8px; border: 1px solid #fcd34d; }}
                .success {{ color: #059669; font-weight: bold; padding: 10px; background: #d1fae5; border-radius: 5px; }}
                .error {{ color: #dc2626; font-weight: bold; padding: 10px; background: #fee2e2; border-radius: 5px; }}
                pre {{ margin: 0; white-space: pre-wrap; word-break: break-all; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>
                    <span>🤖 Execution Report</span>
                    <span class="task-badge">Task ID: {self.task_id}</span>
                </h1>
                <div class="meta">
                    <p><strong>Goal:</strong> {self.task_description}</p>
                    <p>
                        <strong>Date:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | 
                        <strong>Duration:</strong> {duration}s |
                        <strong style="color:#d97706; margin-left:15px;">
                            {COIN_SVG} Total Tokens: {self.total_tokens}
                        </strong>
                    </p>
                </div>
                <div class="logs">
        """
        
        for log in self.logs:
            token_val = log.get("tokens")
            token_html = f'<span class="token-tag" title="Token Usage">{COIN_SVG}{token_val}</span>' if token_val else ""

            if log['type'] == 'planner':
                html_content += f"""<div class="log-entry planner"><h4>🧠 Planning {token_html}</h4><details><summary>Details</summary><pre>{log['output']}</pre></details></div>"""
            elif log['type'] == 'step_start':
                html_content += f"""<div class="log-entry step-start"><h3>📍 {log['title']}</h3></div>"""
            elif log['type'] == 'vision_attempt':
                html_content += f"""<div class="vision-attempt"><div class="vision-left"><span class="badge badge-retry">Attempt #{log['retry']}</span>{token_html}<div style="margin-top:5px;font-size:0.8em;color:#888;">{log['time']}</div><a href="{log['image']}" target="_blank"><img src="{log['image']}" class="screenshot"></a></div><div class="vision-right"><div><strong>Thought:</strong></div><div class="response-box">{log['response']}</div><div style="margin-top:10px;"><strong>Action:</strong></div><pre style="background:#333;color:#fff;padding:10px;">{log['action']}</pre></div></div>"""
            elif log['type'] == 'critic_check':
                status = "success" if log['success'] else "error"
                color = "#059669" if log['success'] else "#dc2626"
                bg = "#f0fdf4" if log['success'] else "#fef2f2"
                html_content += f"""<div class="vision-attempt" style="border-left:4px solid {color};background:{bg};"><div class="vision-left"><span class="badge badge-critic">Critic</span>{token_html}<div style="margin-top:5px;font-size:0.8em;color:#888;">{log['time']}</div><a href="{log['image']}" target="_blank"><img src="{log['image']}" class="screenshot"></a></div><div class="vision-right"><div class="{status}">{ "✅ PASS" if log['success'] else "❌ FAIL" }: {log['reason']}</div></div></div>"""
            elif log['type'] == 'success':
                html_content += f'<div class="log-entry success">🎉 {log["msg"]}</div>'
            elif log['type'] == 'error':
                html_content += f'<div class="log-entry error">⛔ {log["msg"]}</div>'

        html_content += "</div></div></body></html>"
        
        # 【关键修改】生成 HTML 文件名，带上 task_id，存放在 base_dir 下
        report_filename = f"task_{self.task_id}_report.html"
        report_path = os.path.join(self.base_dir, report_filename)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        return report_path