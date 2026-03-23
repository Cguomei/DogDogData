"""
测试执行脚本 - 运行所有测试并生成报告
使用方法：python run_tests.py
"""
import subprocess
import sys
import os
from datetime import datetime


def run_tests():
    """运行 pytest 并生成详细报告"""
    print("=" * 70)
    print("开始执行测试套件")
    print("=" * 70)
    
    # 创建 reports 目录
    os.makedirs('Test/reports', exist_ok=True)
    
    # 生成时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 运行 pytest 的命令
    cmd = [
        sys.executable, '-m', 'pytest',
        'Test/',  # 测试目录
        '-v',  # 详细输出
        '--tb=short',  # 简短的 traceback
        f'--html=Test/reports/report_{timestamp}.html',  # HTML 报告
        f'--self-contained-html',  # 独立的 HTML 文件
        '--junitxml=Test/reports/junit_report.xml',  # JUnit XML 格式
        '-s',  # 不捕获标准输出
        '--capture=sys'  # 捕获 sys.stdout
    ]
    
    print(f"执行命令：{' '.join(cmd)}")
    print("-" * 70)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 打印测试结果
        print(result.stdout)
        if result.stderr:
            print("错误信息:")
            print(result.stderr)
        
        # 返回码为 0 表示所有测试通过
        if result.returncode == 0:
            print("\n✓ 所有测试通过!")
        else:
            print(f"\n✗ 部分测试失败，退出码：{result.returncode}")
            
        return result.returncode
        
    except Exception as e:
        print(f"运行测试时发生错误：{e}")
        return 1


def generate_summary():
    """生成测试总结"""
    print("\n" + "=" * 70)
    print("测试执行完成")
    print("=" * 70)
    print(f"报告已保存到：Test/reports/")
    print("包含以下文件:")
    print("  - report_*.html : HTML 格式的测试报告")
    print("  - junit_report.xml : JUnit 格式的测试报告")
    print("=" * 70)


if __name__ == '__main__':
    exit_code = run_tests()
    generate_summary()
    sys.exit(exit_code)
