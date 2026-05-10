#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能测试控制台 - 后端服务
提供REST API供前端调用，执行各种测试任务
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import subprocess
import threading
import json
import os
import sys
from datetime import datetime
import queue
import time

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 测试输出队列
test_output_queue = queue.Queue()
# 当前测试状态
test_status = {
    'running': False,
    'current_test': None,
    'start_time': None,
    'output_lines': []
}

def get_project_root():
    """获取项目根目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_command_async(command, test_name):
    """异步运行命令并捕获输出"""
    def run():
        try:
            test_status['running'] = True
            test_status['current_test'] = test_name
            test_status['start_time'] = datetime.now().isoformat()
            test_status['output_lines'] = []
            
            add_output(f"▶ 开始执行: {test_name}", "info")
            add_output(f"命令: {' '.join(command)}", "info")
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=get_project_root(),
                bufsize=1,
                universal_newlines=True
            )
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    line = line.rstrip()
                    test_status['output_lines'].append(line)
                    
                    # 判断行类型
                    line_type = "info"
                    if "PASSED" in line or "passed" in line:
                        line_type = "success"
                    elif "FAILED" in line or "failed" in line or "ERROR" in line:
                        line_type = "error"
                    elif "warning" in line.lower():
                        line_type = "warning"
                    
                    add_output(line, line_type)
            
            process.wait()
            
            if process.returncode == 0:
                add_output(f"✅ {test_name} 完成！", "success")
            else:
                add_output(f"❌ {test_name} 失败 (退出码: {process.returncode})", "error")
            
            test_status['running'] = False
            test_status['current_test'] = None
            
        except Exception as e:
            add_output(f"❌ 执行错误: {str(e)}", "error")
            test_status['running'] = False
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

def add_output(text, line_type="info"):
    """添加输出到队列"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    test_output_queue.put({
        'timestamp': timestamp,
        'text': text,
        'type': line_type
    })

@app.route('/')
def index():
    """提供前端页面"""
    return send_from_directory('.', 'test_console.html')

@app.route('/api/status')
def get_status():
    """获取测试状态"""
    return jsonify({
        'running': test_status['running'],
        'current_test': test_status['current_test'],
        'start_time': test_status['start_time']
    })

@app.route('/api/output')
def get_output():
    """获取测试输出"""
    lines = []
    while not test_output_queue.empty():
        try:
            lines.append(test_output_queue.get_nowait())
        except queue.Empty:
            break
    return jsonify(lines)

@app.route('/api/test/full', methods=['POST'])
def run_full_tests():
    """运行全面测试"""
    if test_status['running']:
        return jsonify({'error': '已有测试正在运行'}), 400
    
    cmd = [sys.executable, 'Test/run_full_tests.py']
    run_command_async(cmd, "全面测试套件")
    
    return jsonify({'message': '测试已启动'})

@app.route('/api/test/api', methods=['POST'])
def run_api_tests():
    """运行API测试"""
    if test_status['running']:
        return jsonify({'error': '已有测试正在运行'}), 400
    
    cmd = [
        sys.executable, '-m', 'pytest',
        'Test/api_tests/',
        '-v', '--tb=short', '-q'
    ]
    run_command_async(cmd, "API测试")
    
    return jsonify({'message': '测试已启动'})

@app.route('/api/test/ui', methods=['POST'])
def run_ui_tests():
    """运行UI测试"""
    if test_status['running']:
        return jsonify({'error': '已有测试正在运行'}), 400
    
    cmd = [
        sys.executable, '-m', 'pytest',
        'Test/ui_tests/',
        '-v', '--tb=short', '-q'
    ]
    run_command_async(cmd, "UI测试 (Playwright)")
    
    return jsonify({'message': '测试已启动'})

@app.route('/api/test/e2e', methods=['POST'])
def run_e2e_tests():
    """运行E2E测试"""
    if test_status['running']:
        return jsonify({'error': '已有测试正在运行'}), 400
    
    cmd = [
        sys.executable, '-m', 'pytest',
        'Test/e2e_tests/',
        '-v', '--tb=short', '-q'
    ]
    run_command_async(cmd, "E2E端到端测试")
    
    return jsonify({'message': '测试已启动'})

@app.route('/api/test/coverage', methods=['POST'])
def generate_coverage():
    """生成覆盖率报告"""
    if test_status['running']:
        return jsonify({'error': '已有测试正在运行'}), 400
    
    cmd = [
        sys.executable, '-m', 'pytest',
        'Test/api_tests/test_ai_assistant.py',
        '--cov=routes.ai_assistant',
        '--cov-report=html',
        '--cov-report=term-missing',
        '-q'
    ]
    run_command_async(cmd, "代码覆盖率分析")
    
    return jsonify({'message': '覆盖率分析已启动'})

@app.route('/api/test/module/<module_name>', methods=['POST'])
def run_module_test(module_name):
    """运行特定模块测试"""
    if test_status['running']:
        return jsonify({'error': '已有测试正在运行'}), 400
    
    module_map = {
        'ai_assistant': 'Test/api_tests/test_ai_assistant.py',
        'feedback': 'Test/api_tests/test_feedback.py',
        'data_analysis': 'Test/api_tests/test_data_analysis_api.py',
        'internationalization': 'Test/api_tests/test_internationalization.py',
        'breeds': 'Test/api_tests/test_breeds_api.py',
        'monitoring': 'Test/api_tests/test_monitoring.py'
    }
    
    test_file = module_map.get(module_name)
    if not test_file:
        return jsonify({'error': f'未知模块: {module_name}'}), 404
    
    cmd = [
        sys.executable, '-m', 'pytest',
        test_file,
        '-v', '--tb=short', '-q'
    ]
    
    module_names = {
        'ai_assistant': 'AI智能助手',
        'feedback': '用户反馈',
        'data_analysis': '数据分析',
        'internationalization': '国际化',
        'breeds': '品种管理',
        'monitoring': '系统监控'
    }
    
    test_name = f"{module_names.get(module_name, module_name)} 测试"
    run_command_async(cmd, test_name)
    
    return jsonify({'message': '测试已启动'})

@app.route('/api/reports/list')
def list_reports():
    """列出所有测试报告"""
    reports_dir = os.path.join(get_project_root(), 'Test', 'reports')
    reports = []
    
    if os.path.exists(reports_dir):
        for file in os.listdir(reports_dir):
            if file.endswith(('.html', '.md')):
                file_path = os.path.join(reports_dir, file)
                stat = os.stat(file_path)
                reports.append({
                    'name': file,
                    'path': file_path,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
    
    reports.sort(key=lambda x: x['modified'], reverse=True)
    return jsonify(reports)

@app.route('/api/stats')
def get_stats():
    """获取测试统计信息"""
    # 这里可以从最近的测试报告中解析数据
    # 暂时返回模拟数据
    return jsonify({
        'total_tests': 178,
        'passed': 178,
        'failed': 0,
        'pass_rate': 100.0,
        'execution_time': 51,
        'coverage': 75,
        'last_run': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🧪 智能测试控制台 - 后端服务")
    print("=" * 60)
    print(f"📍 项目路径: {get_project_root()}")
    print(f"🌐 访问地址: http://localhost:5555")
    print("=" * 60)
    print("\n💡 提示:")
    print("   1. 在浏览器中打开 http://localhost:5555")
    print("   2. 点击按钮即可运行测试")
    print("   3. 实时查看测试输出")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5555, debug=True)
