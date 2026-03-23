"""
测试质量检查工具
检测测试配置、依赖、代码质量等问题，并生成修复建议
"""
import os
import sys
from pathlib import Path
from datetime import datetime


class TestQualityChecker:
    """测试质量检查器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dir = self.project_root / 'Test'
        self.issues = []
        self.warnings = []
        self.suggestions = []
        
    def check_all(self):
        """执行所有检查"""
        print("=" * 80)
        print("🔍 测试质量检查开始")
        print("=" * 80)
        print()
        
        self.check_pytest_config()
        self.check_test_dependencies()
        self.check_test_framework()
        self.check_conftest()
        self.check_test_files()
        self.check_reports_directory()
        self.check_environment()
        
        self.generate_report()
        
    def check_pytest_config(self):
        """检查 pytest 配置"""
        print("1️⃣  检查 pytest 配置...")
        
        pytest_ini = self.project_root / 'pytest.ini'
        if not pytest_ini.exists():
            self.issues.append({
                'type': 'CRITICAL',
                'item': 'pytest.ini',
                'problem': '配置文件不存在',
                'solution': '创建 pytest.ini 文件'
            })
            return
        
        with open(pytest_ini, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查 testpaths 配置
        if 'testpaths = tests' in content:
            self.issues.append({
                'type': 'ERROR',
                'item': 'pytest.ini - testpaths',
                'problem': '测试路径配置错误，应该是 "Test" 而不是 "tests"',
                'solution': '修改为：testpaths = Test/'
            })
        
        # 检查 pythonpath
        if 'pythonpath' not in content:
            self.warnings.append({
                'type': 'WARNING',
                'item': 'pytest.ini - pythonpath',
                'problem': '缺少 pythonpath 配置，可能导致导入失败',
                'solution': '添加：pythonpath = .'
            })
        
        print(f"   ✓ pytest.ini 存在")
        print()
    
    def check_test_dependencies(self):
        """检查测试依赖"""
        print("2️⃣  检查测试依赖...")
        
        req_test_file = self.test_dir / 'requirements-test.txt'
        if not req_test_file.exists():
            self.warnings.append({
                'type': 'WARNING',
                'item': 'requirements-test.txt',
                'problem': '测试依赖文件不存在',
                'solution': '创建 requirements-test.txt 文件'
            })
            return
        
        # 检查关键依赖
        with open(req_test_file, 'r', encoding='utf-8') as f:
            content = f.read().lower()
        
        critical_deps = ['pytest', 'pytest-flask']
        for dep in critical_deps:
            if dep not in content:
                self.warnings.append({
                    'type': 'WARNING',
                    'item': f'requirements-test.txt - {dep}',
                    'problem': f'缺少关键依赖：{dep}',
                    'solution': f'添加：{dep}>=7.0.0'
                })
        
        print(f"   ✓ requirements-test.txt 存在")
        print()
    
    def check_test_framework(self):
        """检查测试框架"""
        print("3️⃣  检查测试框架...")
        
        framework_file = self.test_dir / 'test_framework.py'
        if not framework_file.exists():
            self.issues.append({
                'type': 'ERROR',
                'item': 'test_framework.py',
                'problem': '测试框架文件不存在',
                'solution': '创建 test_framework.py 文件'
            })
            return
        
        with open(framework_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键类
        if 'class TestExecutionManager' not in content:
            self.issues.append({
                'type': 'ERROR',
                'item': 'test_framework.py',
                'problem': '缺少 TestExecutionManager 类',
                'solution': '实现测试执行管理器'
            })
        
        # 检查 pytest hooks
        if 'def pytest_configure' not in content:
            self.warnings.append({
                'type': 'WARNING',
                'item': 'test_framework.py',
                'problem': '缺少 pytest_configure hook',
                'solution': '添加 pytest_configure 函数'
            })
        
        print(f"   ✓ test_framework.py 存在")
        print()
    
    def check_conftest(self):
        """检查 conftest.py"""
        print("4️⃣  检查 conftest.py...")
        
        conftest_file = self.test_dir / 'conftest.py'
        if not conftest_file.exists():
            self.issues.append({
                'type': 'CRITICAL',
                'item': 'conftest.py',
                'problem': 'pytest fixture 配置文件不存在',
                'solution': '创建 conftest.py 文件'
            })
            return
        
        with open(conftest_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键 fixture
        required_fixtures = ['app', 'client', 'db', 'logged_in_client', 'admin_client']
        for fixture in required_fixtures:
            if f'def {fixture}(' not in content:
                self.warnings.append({
                    'type': 'WARNING',
                    'item': f'conftest.py - {fixture}',
                    'problem': f'缺少 fixture: {fixture}',
                    'solution': f'添加 {fixture} fixture'
                })
        
        # 检查导入
        if 'from app import app' not in content:
            self.issues.append({
                'type': 'ERROR',
                'item': 'conftest.py - imports',
                'problem': '导入错误的 app 模块',
                'solution': '确保使用：from app import app'
            })
        
        print(f"   ✓ conftest.py 存在")
        print()
    
    def check_test_files(self):
        """检查测试文件"""
        print("5️⃣  检查测试文件...")
        
        test_files = ['test_auth.py', 'test_breed.py']
        for test_file in test_files:
            file_path = self.test_dir / test_file
            if not file_path.exists():
                self.warnings.append({
                    'type': 'WARNING',
                    'item': test_file,
                    'problem': '测试文件不存在',
                    'solution': f'创建 {test_file} 文件'
                })
                continue
            
            # 检查文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否导入 test_framework
            if 'from test_framework import' not in content:
                self.suggestions.append({
                    'type': 'SUGGESTION',
                    'item': test_file,
                    'problem': '未使用统一的测试框架',
                    'solution': '导入并使用 test_framework'
                })
            
            # 检查测试函数数量
            test_count = content.count('def test_')
            if test_count == 0:
                self.warnings.append({
                    'type': 'WARNING',
                    'item': test_file,
                    'problem': '没有测试函数',
                    'solution': '添加测试用例'
                })
            else:
                print(f"   ✓ {test_file}: {test_count} 个测试用例")
        
        print()
    
    def check_reports_directory(self):
        """检查报告目录"""
        print("6️⃣  检查报告目录...")
        
        reports_dir = self.test_dir / 'reports'
        if not reports_dir.exists():
            self.warnings.append({
                'type': 'WARNING',
                'item': 'reports/',
                'problem': '报告目录不存在',
                'solution': '创建 reports 目录'
            })
            return
        
        # 检查是否有报告生成
        json_reports = list(reports_dir.glob('test_report_*.json'))
        if not json_reports:
            self.suggestions.append({
                'type': 'SUGGESTION',
                'item': 'reports/',
                'problem': '还没有生成测试报告',
                'solution': '运行测试以生成报告'
            })
        
        print(f"   ✓ reports/ 目录存在")
        print()
    
    def check_environment(self):
        """检查环境配置"""
        print("7️⃣  检查环境配置...")
        
        env_file = self.project_root / '.env'
        if not env_file.exists():
            self.warnings.append({
                'type': 'WARNING',
                'item': '.env',
                'problem': '环境变量配置文件不存在',
                'solution': '创建 .env 文件并配置数据库连接'
            })
            return
        
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查数据库配置
        db_configs = ['DB_USER', 'DB_PASSWORD', 'DB_NAME']
        for config in db_configs:
            if config not in content:
                self.warnings.append({
                    'type': 'WARNING',
                    'item': f'.env - {config}',
                    'problem': f'缺少数据库配置：{config}',
                    'solution': f'添加 {config} 配置'
                })
        
        print(f"   ✓ .env 文件存在")
        print()
    
    def generate_report(self):
        """生成检查报告"""
        print("=" * 80)
        print("📊 检查结果汇总")
        print("=" * 80)
        print()
        
        total_issues = len(self.issues) + len(self.warnings) + len(self.suggestions)
        
        if total_issues == 0:
            print("✅ 所有检查通过！测试环境配置完美。")
        else:
            print(f"发现 {total_issues} 个问题/建议:")
            print(f"  ❌ 严重问题：{len([i for i in self.issues if i['type'] == 'CRITICAL'])}")
            print(f"  🚫 错误：{len([i for i in self.issues if i['type'] == 'ERROR'])}")
            print(f"  ⚠️  警告：{len(self.warnings)}")
            print(f"  💡 建议：{len(self.suggestions)}")
            print()
        
        # 打印严重问题和错误
        critical_and_errors = [i for i in self.issues if i['type'] in ['CRITICAL', 'ERROR']]
        if critical_and_errors:
            print("-" * 80)
            print("需要立即修复的问题:")
            print("-" * 80)
            for issue in critical_and_errors:
                print(f"\n[{issue['type']}] {issue['item']}")
                print(f"  问题：{issue['problem']}")
                print(f"  解决：{issue['solution']}")
            print()
        
        # 打印警告
        if self.warnings:
            print("-" * 80)
            print("警告（建议修复）:")
            print("-" * 80)
            for warning in self.warnings[:5]:  # 只显示前 5 个
                print(f"\n[WARNING] {warning['item']}")
                print(f"  问题：{warning['problem']}")
                print(f"  解决：{warning['solution']}")
            if len(self.warnings) > 5:
                print(f"\n... 还有 {len(self.warnings) - 5} 个警告")
            print()
        
        # 打印建议
        if self.suggestions:
            print("-" * 80)
            print("改进建议:")
            print("-" * 80)
            for suggestion in self.suggestions[:5]:  # 只显示前 5 个
                print(f"\n[SUGGESTION] {suggestion['item']}")
                print(f"  当前：{suggestion['problem']}")
                print(f"  建议：{suggestion['solution']}")
            if len(self.suggestions) > 5:
                print(f"\n... 还有 {len(self.suggestions) - 5} 个建议")
            print()
        
        # 保存报告
        self.save_report()
        
        print("=" * 80)
        print("检查完成!")
        print("=" * 80)
    
    def save_report(self):
        """保存检查报告"""
        report_dir = self.test_dir / 'reports'
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f'quality_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("测试质量检查报告\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"总计发现问题：{len(self.issues) + len(self.warnings) + len(self.suggestions)}\n")
            f.write(f"  严重问题：{len([i for i in self.issues if i['type'] == 'CRITICAL'])}\n")
            f.write(f"  错误：{len([i for i in self.issues if i['type'] == 'ERROR'])}\n")
            f.write(f"  警告：{len(self.warnings)}\n")
            f.write(f"  建议：{len(self.suggestions)}\n\n")
            
            if self.issues:
                f.write("-" * 80 + "\n")
                f.write("问题列表:\n")
                f.write("-" * 80 + "\n\n")
                for issue in self.issues:
                    f.write(f"[{issue['type']}] {issue['item']}\n")
                    f.write(f"  问题：{issue['problem']}\n")
                    f.write(f"  解决：{issue['solution']}\n\n")
            
            if self.warnings:
                f.write("-" * 80 + "\n")
                f.write("警告列表:\n")
                f.write("-" * 80 + "\n\n")
                for warning in self.warnings:
                    f.write(f"[WARNING] {warning['item']}\n")
                    f.write(f"  问题：{warning['problem']}\n")
                    f.write(f"  解决：{warning['solution']}\n\n")
            
            if self.suggestions:
                f.write("-" * 80 + "\n")
                f.write("建议列表:\n")
                f.write("-" * 80 + "\n\n")
                for suggestion in self.suggestions:
                    f.write(f"[SUGGESTION] {suggestion['item']}\n")
                    f.write(f"  当前：{suggestion['problem']}\n")
                    f.write(f"  建议：{suggestion['solution']}\n\n")
        
        print(f"📄 详细报告已保存：{report_file}")


if __name__ == '__main__':
    checker = TestQualityChecker()
    checker.check_all()
