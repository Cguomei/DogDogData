"""
专业测试执行脚本
生成详细的测试报告和缺陷跟踪记录
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_tests(test_file=None, verbose=True):
    """
    运行测试
    
    Args:
        test_file: 指定测试文件，None 表示运行所有测试
        verbose: 是否显示详细输出
    """
    print("=" * 80)
    print("🧪 狗狗数据分析系统 - 自动化测试执行")
    print("=" * 80)
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 构建 pytest 命令
    cmd = [
        sys.executable, '-m', 'pytest',
        'Test/',  # 测试目录
        '-v',     # 详细输出
        '--tb=short',  # 简化 traceback
        '--strict-markers'
    ]
    
    # 如果指定了测试文件
    if test_file:
        cmd = [
            sys.executable, '-m', 'pytest',
            f'Test/{test_file}',
            '-v',
            '--tb=short'
        ]
    
    # 添加覆盖率选项（如果安装了 pytest-cov）
    try:
        import pytest_cov
        cmd.extend(['--cov=app', '--cov-report=html:Test/reports/coverage'])
    except ImportError:
        pass
    
    print(f"执行命令：{' '.join(cmd)}")
    print("-" * 80)
    print()
    
    # 执行测试
    result = subprocess.run(cmd, capture_output=False, encoding='utf-8')
    
    print()
    print("=" * 80)
    if result.returncode == 0:
        print("✅ 所有测试通过！")
    else:
        print(f"❌ {result.returncode} 个测试失败")
    print("=" * 80)
    
    return result.returncode


def generate_html_report():
    """生成 HTML 测试报告"""
    from pathlib import Path
    import json
    
    report_dir = Path('Test/reports')
    report_dir.mkdir(exist_ok=True)
    
    # 查找最新的 JSON 报告
    json_reports = list(report_dir.glob('test_report_*.json'))
    if not json_reports:
        print("⚠️  未找到测试报告")
        return
    
    latest_report = max(json_reports, key=lambda p: p.stat().st_mtime)
    
    with open(latest_report, 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    # 生成 HTML 报告
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>测试报告 - {report_data['summary']['start_time'][:10]}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .pass {{ color: #28a745; }}
        .fail {{ color: #dc3545; }}
        .skip {{ color: #ffc107; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>🧪 测试报告</h1>
    
    <div class="summary">
        <h2>摘要</h2>
        <p><strong>总测试数:</strong> {report_data['summary']['total']}</p>
        <p><strong class="pass">✅ 通过:</strong> {report_data['summary']['passed']}</p>
        <p><strong class="fail">❌ 失败:</strong> {report_data['summary']['failed']}</p>
        <p><strong class="skip">⏭️ 跳过:</strong> {report_data['summary']['skipped']}</p>
        <p><strong>通过率:</strong> {report_data['summary']['pass_rate']}</p>
        <p><strong>耗时:</strong> {report_data['summary']['duration']:.2f}秒</p>
        <p><strong>生成时间:</strong> {report_data['generated_at']}</p>
    </div>
    
    <h2>测试结果详情</h2>
    <table>
        <tr>
            <th>测试 ID</th>
            <th>测试名称</th>
            <th>模块</th>
            <th>优先级</th>
            <th>状态</th>
            <th>耗时 (s)</th>
            <th>错误信息</th>
        </tr>
"""
    
    for result in report_data['results']:
        status_class = 'pass' if result['status'] == 'PASS' else 'fail' if result['status'] == 'FAIL' else 'skip'
        status_icon = '✅' if result['status'] == 'PASS' else '❌' if result['status'] == 'FAIL' else '⏭️'
        
        html_content += f"""
        <tr>
            <td>{result['test_id']}</td>
            <td>{result['test_name']}</td>
            <td>{result['module']}</td>
            <td>{result['priority']}</td>
            <td class="{status_class}">{status_icon} {result['status']}</td>
            <td>{result['execution_time']:.3f}</td>
            <td>{result.get('error_message', '') or '-'}</td>
        </tr>
"""
    
    html_content += """
    </table>
</body>
</html>
"""
    
    html_file = report_dir / f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📄 HTML 报告已生成：{html_file}")
    return html_file


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='运行自动化测试')
    parser.add_argument('--file', '-f', help='指定测试文件')
    parser.add_argument('--html', action='store_true', help='生成 HTML 报告')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    
    args = parser.parse_args()
    
    exit_code = run_tests(args.file if args.file else None)
    
    if args.html or args.all:
        generate_html_report()
    
    sys.exit(exit_code)
