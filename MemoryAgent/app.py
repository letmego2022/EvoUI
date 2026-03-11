import json
import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify
import os
from datetime import datetime
from flask import render_template, abort, send_from_directory
import shutil


app = Flask(__name__)
app.secret_key = 'your_very_secret_key'

SCENARIOS_DIR = 'scenarios'

# 确保 scenarios 目录存在
if not os.path.exists(SCENARIOS_DIR):
    os.makedirs(SCENARIOS_DIR)

def get_scenario_path(filename):
    """安全地获取场景文件的路径"""
    # 基本的安全检查，防止目录遍历攻击
    if '..' in filename or filename.startswith('/'):
        return None
    return os.path.join(SCENARIOS_DIR, filename)

def load_data(filename):
    """从指定的JSON文件加载数据"""
    filepath = get_scenario_path(filename)
    if not filepath or not os.path.exists(filepath):
        abort(404, description=f"文件 {filename} 未找到。")
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(filename, data):
    """将数据保存到指定的JSON文件"""
    filepath = get_scenario_path(filename)
    if not filepath:
        abort(400, description="无效的文件名。")
    # 更新 'updated_at' 字段
    data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    """主页，显示 scenarios 目录下的所有 .json 文件及其元数据"""
    scenarios_info = []
    
    # 遍历 scenarios 目录下的所有文件
    for filename in sorted(os.listdir(SCENARIOS_DIR)):
        if filename.endswith('.json'):
            filepath = os.path.join(SCENARIOS_DIR, filename)
            try:
                # 获取文件最后修改时间
                last_modified_timestamp = os.path.getmtime(filepath)
                last_modified_str = datetime.fromtimestamp(last_modified_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                
                # 读取JSON文件以获取 workspace 和操作数量
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    workspace = data.get('workspace', 'N/A')
                    op_count = len(data.get('operations', {}))
                
                scenarios_info.append({
                    'filename': filename,
                    'workspace': workspace,
                    'op_count': op_count,
                    'last_modified': last_modified_str
                })
            except (IOError, json.JSONDecodeError) as e:
                # 如果文件读取或解析失败，也显示出来，方便排错
                scenarios_info.append({
                    'filename': filename,
                    'workspace': '读取错误',
                    'op_count': 'N/A',
                    'last_modified': f'错误: {e}',
                    'error': True
                })

    return render_template('index.html', scenarios=scenarios_info)

@app.route('/edit/<filename>')
def edit_scenario(filename):
    """编辑指定场景文件的页面"""
    data = load_data(filename)
    return render_template('edit.html', data=data, filename=filename)

@app.route('/update/<filename>', methods=['POST'])
def update_scenario(filename):
    """处理编辑表单的提交，只更新 operations"""
    data = load_data(filename)
    form_data = request.form

    # 识别表单中存在的所有 operation IDs
    op_ids = {key.split('_')[1] for key in form_data if key.startswith('op_')}

    # 创建一个新的 operations 字典来存放更新后的数据
    updated_operations = {}

    for op_id in op_ids:
        # 如果这个op的描述字段不存在，可能意味着它已经被其他请求删除，跳过它
        if f'op_{op_id}_description' not in form_data:
            continue

        op_data = data['operations'].get(op_id, {}) # 获取原始数据以保留未编辑的字段
        op_data['description'] = form_data.get(f'op_{op_id}_description')
        op_data['assertion'] = form_data.get(f'op_{op_id}_assertion')
        
        # 更新 actions
        updated_actions = []
        action_index = 0
        while True:
            # 检查下一个 action 是否存在于表单中
            action_key = f'op_{op_id}_action_{action_index}_action'
            if action_key not in form_data:
                break
            
            action_item = op_data['actions'][action_index] # 获取原始action以保留结构
            action_item['action'] = form_data.get(action_key)
            action_item['coordinate']['x'] = float(form_data.get(f'op_{op_id}_action_{action_index}_coord_x', 0))
            action_item['coordinate']['y'] = float(form_data.get(f'op_{op_id}_action_{action_index}_coord_y', 0))
            action_item['text'] = form_data.get(f'op_{op_id}_action_{action_index}_text', '')
            action_item['description'] = form_data.get(f'op_{op_id}_action_{action_index}_description')
            updated_actions.append(action_item)
            action_index += 1
        
        op_data['actions'] = updated_actions
        updated_operations[op_id] = op_data

    # 用更新后的 operations 替换旧的
    data['operations'] = updated_operations
    
    save_data(filename, data)
    flash(f'文件 {filename} 的操作已成功保存！', 'success')
    return redirect(url_for('edit_scenario', filename=filename))

@app.route('/op/add/<filename>', methods=['POST'])
def add_op(filename):
    """为指定文件添加一个新的 Operation"""
    data = load_data(filename)
    new_op_id = f"op_{uuid.uuid4().hex[:8]}"
    
    data.setdefault('operations', {})[new_op_id] = {
      "description": "新的操作描述",
      "actions": [],
      "assertion": "新的断言",
      "stats": { "success": 0, "fail": 0 },
      "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
      "last_used": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_data(filename, data)
    flash(f'已为 {filename} 添加新操作 {new_op_id}！', 'success')
    return redirect(url_for('edit_scenario', filename=filename))

@app.route('/op/delete/<filename>/<op_id>', methods=['POST'])
def delete_op(filename, op_id):
    """删除一个 Operation"""
    data = load_data(filename)
    if 'operations' in data and op_id in data['operations']:
        del data['operations'][op_id]
        save_data(filename, data)
        flash(f'操作 {op_id} 已从 {filename} 中删除。', 'success')
    else:
        flash(f'在 {filename} 中未找到操作 {op_id}。', 'danger')
    return redirect(url_for('edit_scenario', filename=filename))

@app.route('/test_reports')
def test_reports():
    """展示所有测试报告列表"""
    reports_dir = './test_reports'
    reports = []
    
    if os.path.exists(reports_dir):
        for item in sorted(os.listdir(reports_dir), reverse=True):  # 最新的在前面
            if item.startswith('run_') and os.path.isdir(os.path.join(reports_dir, item)):
                report_path = os.path.join(reports_dir, item, 'report.html')
                if os.path.exists(report_path):
                    # 获取目录修改时间作为报告时间
                    mtime = os.path.getmtime(os.path.join(reports_dir, item))
                    reports.append({
                        'dirname': item,
                        'name': item.replace('run_', '测试运行_'),
                        'created': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'path': f'{item}/report.html'
                    })
    
    return render_template('test_reports.html', reports=reports)

@app.route('/test_reports/<path:filename>')
def serve_report(filename):
    """提供报告文件访问"""
    return send_from_directory('./test_reports', filename)

@app.route('/test_reports/delete/<dirname>', methods=['POST'])
def delete_report(dirname):
    reports_dir = './test_reports'
    target_path = os.path.join(reports_dir, dirname)

    if not dirname.startswith('run_'):
        return jsonify({"success": False})

    if os.path.exists(target_path) and os.path.isdir(target_path):
        shutil.rmtree(target_path)
        return jsonify({"success": True})

    return jsonify({"success": False})

if __name__ == '__main__':
    app.run(debug=True, port=8001, host='0.0.0.0')