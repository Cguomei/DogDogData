"""
统一测试运行脚本
支持运行 API、UI、E2E 测试，并生成综合报告
"""
import subprocess
import sys
import os
from datetime import datetime


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.test_root = os.path.join(os.path.dirname(__file__), '..')
        self.reports_dir = os.path.join(self.test_root, 'reports')
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # 时间戳用于报告命名
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def run_tests(self, test_path, report_name, extra_args=None):
        """运行指定路径的测试"""
        if extra_args is None:
            extra_args = []
        
        report_path = os.path.join(self.reports_dir, f"{report_name}_{self.timestamp}.html")
        
        cmd = [
            sys.executable, '-m', 'pytest',
            test_path,
            '-v',
            '--tb=short',
            '-s',
            f'--html={report_path}',
            '--self-contained-html',
        ] + extra_args
        
        print(f"\n{'='*60}")
        print(f"运行测试: {test_path}")
        print(f"报告路径: {report_path}")
        print(f"{'='*60}\n")
        
        result = subprocess.run(cmd, cwd=self.test_root)
        return result.returncode == 0
    
    def run_api_tests(self):
        """运行所有 API 测试"""
        print("\n🔧 开始运行 API 测试...")
        return self.run_tests(
            'Test/api_tests/',
            'api_tests',
            ['-m', 'not playwright']
        )
    
    def run_ui_tests(self):
        """运行所有 UI 测试"""
        print("\n🎨 开始运行 UI 测试...")
        return self.run_tests(
            'Test/ui_tests/',
            'ui_tests',
            ['-m', 'playwright']
        )
    
    def run_e2e_tests(self):
        """运行端到端测试"""
        print("\n🔄 开始运行 E2E 集成测试...")
        return self.run_tests(
            'Test/e2e_tests/',
            'e2e_tests'
        )
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n🚀 开始运行全部测试套件...")
        return self.run_tests(
            'Test/',
            'all_tests'
        )
    
    def run_smoke_tests(self):
        """运行冒烟测试（核心功能快速验证）"""
        print("\n💨 开始运行冒烟测试...")
        # 只运行标记为 P0 的测试
        return self.run_tests(
            'Test/',
            'smoke_tests',
            ['-m', 'p0', '-x']  # -x 遇到第一个失败就停止
        )
    
    def generate_summary_report(self, results):
        """生成测试总结报告"""
        summary_path = os.path.join(self.reports_dir, f'test_summary_{self.timestamp}.txt')
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("自动化测试执行总结报告\n")
            f.write(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            for test_type, success in results.items():
                status = "✅ 通过" if success else "❌ 失败"
                f.write(f"{test_type}: {status}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("详细报告请查看 reports 目录下的 HTML 文件\n")
            f.write("=" * 80 + "\n")
        
        print(f"\n📊 测试总结报告已生成: {summary_path}")
        return summary_path


def main():
    """主函数"""
    runner = TestRunner()
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
    else:
        test_type = 'all'
    
    results = {}
    
    if test_type == 'api':
        results['API 测试'] = runner.run_api_tests()
    elif test_type == 'ui':
        results['UI 测试'] = runner.run_ui_tests()
    elif test_type == 'e2e':
        results['E2E 测试'] = runner.run_e2e_tests()
    elif test_type == 'smoke':
        results['冒烟测试'] = runner.run_smoke_tests()
    elif test_type == 'all':
        results['API 测试'] = runner.run_api_tests()
        results['UI 测试'] = runner.run_ui_tests()
        results['E2E 测试'] = runner.run_e2e_tests()
    else:
        print(f"未知测试类型: {test_type}")
        print("可用选项: api, ui, e2e, smoke, all")
        sys.exit(1)
    
    # 生成总结报告
    runner.generate_summary_report(results)
    
    # 检查是否有失败的测试
    failed_tests = [name for name, success in results.items() if not success]
    
    if failed_tests:
        print(f"\n❌ 以下测试套件存在失败: {', '.join(failed_tests)}")
        sys.exit(1)
    else:
        print("\n✅ 所有测试套件执行成功！")
        sys.exit(0)


if __name__ == '__main__':
    main()
