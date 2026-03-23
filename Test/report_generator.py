"""
测试报告生成和统计模块
生成详细的测试分析报告
"""
import os
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict


class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self, test_dir='Test'):
        self.test_dir = Path(test_dir)
        self.reports_dir = self.test_dir / 'reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.test_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'duration': 0,
            'tests': []
        }
    
    def parse_junit_xml(self, xml_file):
        """解析 JUnit XML 报告"""
        import xml.etree.ElementTree as ET
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            testsuites = root
            for testsuite in testsuites.findall('.//testsuite'):
                self.test_results['total'] += int(testsuite.get('tests', 0))
                self.test_results['failed'] += int(testsuite.get('failures', 0))
                self.test_results['errors'] += int(testsuite.get('errors', 0))
                self.test_results['skipped'] += int(testsuite.get('skipped', 0))
                self.test_results['duration'] += float(testsuite.get('time', 0))
                
                # 解析每个测试用例
                for testcase in testsuite.findall('testcase'):
                    test_info = {
                        'classname': testcase.get('classname', ''),
                        'name': testcase.get('name', ''),
                        'time': float(testcase.get('time', 0)),
                        'status': 'passed'
                    }
                    
                    # 检查是否有失败或错误
                    failure = testcase.find('failure')
                    error = testcase.find('error')
                    skipped = testcase.find('skipped')
                    
                    if failure is not None:
                        test_info['status'] = 'failed'
                        test_info['message'] = failure.get('message', '')
                    elif error is not None:
                        test_info['status'] = 'error'
                        test_info['message'] = error.get('message', '')
                    elif skipped is not None:
                        test_info['status'] = 'skipped'
                    
                    self.test_results['tests'].append(test_info)
            
            self.test_results['passed'] = self.test_results['total'] - \
                                         self.test_results['failed'] - \
                                         self.test_results['errors'] - \
                                         self.test_results['skipped']
                                         
        except Exception as e:
            print(f"解析 XML 失败：{e}")
    
    def generate_text_report(self):
        """生成文本格式的报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.reports_dir / f'test_report_{timestamp}.txt'
        
        lines = [
            "=" * 80,
            "测 试 报 告",
            "=" * 80,
            f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "总 结",
            "-" * 80,
            f"总测试数：{self.test_results['total']}",
            f"通过：{self.test_results['passed']}",
            f"失败：{self.test_results['failed']}",
            f"跳过：{self.test_results['skipped']}",
            f"错误：{self.test_results['errors']}",
            f"通过率：{self._calculate_pass_rate():.2f}%",
            f"总耗时：{self.test_results['duration']:.2f} 秒",
            "",
        ]
        
        # 按模块统计
        module_stats = defaultdict(lambda: {'total': 0, 'passed': 0, 'failed': 0})
        for test in self.test_results['tests']:
            module = test['classname'].split('.')[0] if '.' in test['classname'] else 'unknown'
            module_stats[module]['total'] += 1
            if test['status'] == 'passed':
                module_stats[module]['passed'] += 1
            else:
                module_stats[module]['failed'] += 1
        
        lines.extend([
            "按模块统计",
            "-" * 80,
            f"{'模块':<30} {'总数':<10} {'通过':<10} {'失败':<10} {'通过率':<10}",
            "-" * 80,
        ])
        
        for module, stats in sorted(module_stats.items()):
            pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            lines.append(
                f"{module:<30} {stats['total']:<10} {stats['passed']:<10} "
                f"{stats['failed']:<10} {pass_rate:>6.2f}%"
            )
        
        # 失败的测试详情
        failed_tests = [t for t in self.test_results['tests'] if t['status'] in ('failed', 'error')]
        if failed_tests:
            lines.extend([
                "",
                "失 败 测 试 详 情",
                "-" * 80,
            ])
            
            for test in failed_tests:
                lines.extend([
                    f"\n测试：{test['classname']}.{test['name']}",
                    f"状态：{test['status'].upper()}",
                    f"耗时：{test['time']:.3f}秒",
                    f"信息：{test.get('message', 'N/A')}",
                ])
        
        # 最慢的测试 TOP 10
        sorted_tests = sorted(self.test_results['tests'], key=lambda x: x['time'], reverse=True)[:10]
        lines.extend([
            "",
            "最 慢 的 10 个 测 试",
            "-" * 80,
            f"{'测试名称':<60} {'耗时 (秒)':<10}",
            "-" * 80,
        ])
        
        for test in sorted_tests:
            lines.append(f"{test['classname']}.{test['name']:<50} {test['time']:.3f}")
        
        report_text = '\n'.join(lines)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"\n文本报告已保存：{report_file}")
        return report_text
    
    def generate_json_report(self):
        """生成 JSON 格式的报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.reports_dir / f'test_report_{timestamp}.json'
        
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total': self.test_results['total'],
                'passed': self.test_results['passed'],
                'failed': self.test_results['failed'],
                'skipped': self.test_results['skipped'],
                'errors': self.test_results['errors'],
                'pass_rate': self._calculate_pass_rate(),
                'duration': self.test_results['duration']
            },
            'tests': self.test_results['tests']
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"JSON 报告已保存：{report_file}")
        return report_file
    
    def _calculate_pass_rate(self):
        """计算通过率"""
        if self.test_results['total'] == 0:
            return 0.0
        return (self.test_results['passed'] / self.test_results['total']) * 100
    
    def print_summary(self):
        """打印简要总结"""
        print("\n" + "=" * 80)
        print("测试结果摘要")
        print("=" * 80)
        print(f"总测试数：{self.test_results['total']}")
        print(f"✓ 通过：{self.test_results['passed']}")
        print(f"✗ 失败：{self.test_results['failed']}")
        print(f"⊘ 跳过：{self.test_results['skipped']}")
        print(f"！错误：{self.test_results['errors']}")
        print(f"通过率：{self._calculate_pass_rate():.2f}%")
        print(f"总耗时：{self.test_results['duration']:.2f}秒")
        print("=" * 80)


def generate_test_reports():
    """生成所有测试报告"""
    generator = TestReportGenerator()
    
    # 查找最新的 JUnit XML 文件
    reports_dir = Path('Test/reports')
    xml_files = list(reports_dir.glob('junit_*.xml'))
    
    if xml_files:
        latest_xml = max(xml_files, key=lambda p: p.stat().st_mtime)
        print(f"解析报告文件：{latest_xml}")
        generator.parse_junit_xml(latest_xml)
    
    # 生成报告
    generator.generate_text_report()
    generator.generate_json_report()
    generator.print_summary()
    
    return generator


if __name__ == '__main__':
    generate_test_reports()
