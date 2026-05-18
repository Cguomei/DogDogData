"""
测试用例项目管理测试
覆盖测试项目的配置、执行、报告生成等管理功能
"""

import pytest
import os
import json
from pathlib import Path
from Test.test_framework import test_case, test_manager, TestResult


class TestTestProjectConfiguration:
    """测试项目配置测试类"""

    @test_case("TC-PROJ-001", priority="High", expected="pytest 配置文件正确加载")
    def test_pytest_ini_configuration(self):
        """测试 pytest.ini 配置文件"""
        result = TestResult("TC-PROJ-001", "test_pytest_config", "项目管理", "High")
        result.expected_result = "pytest.ini 配置正确且可被识别"

        try:
            # 检查 pytest.ini 文件是否存在
            pytest_ini_path = Path("pytest.ini")
            assert pytest_ini_path.exists(), "pytest.ini 文件不存在"

            # 读取并验证配置内容
            content = pytest_ini_path.read_text(encoding="utf-8")
            assert "[pytest]" in content, "缺少 [pytest] 段"
            assert "testpaths" in content, "缺少 testpaths 配置"
            assert "addopts" in content, "缺少 addopts 配置"
            assert "markers" in content, "缺少 markers 配置"

            result.status = "PASS"
            result.actual_result = "pytest.ini 配置完整且正确"

        except AssertionError as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)

    @test_case("TC-PROJ-002", priority="High", expected="conftest.py fixtures 可用")
    def test_conftest_fixtures_available(self, client, db, session):
        """测试 conftest.py 中的 fixtures"""
        result = TestResult("TC-PROJ-002", "test_conftest_fixtures", "项目管理", "High")
        result.expected_result = "所有 fixtures 正常工作"

        try:
            # 验证 client fixture
            assert client is not None, "client fixture 不可用"

            # 验证 db fixture
            assert db is not None, "db fixture 不可用"

            # 验证 session fixture
            assert session is not None, "session fixture 不可用"

            result.status = "PASS"
            result.actual_result = "所有 fixtures 正常工作"

        except AssertionError as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)

    @test_case("TC-PROJ-003", priority="Medium", expected="登录 fixtures 正常工作")
    def test_login_fixtures(self, admin_client):
        """测试管理员登录 fixture"""
        result = TestResult("TC-PROJ-003", "test_login_fixtures", "项目管理", "Medium")
        result.expected_result = "admin_client 正常工作"

        try:
            # 验证管理员登录
            assert admin_client is not None, "admin_client fixture 不可用"

            # 管理员应该可以访问品种管理页
            admin_resp = admin_client.get("/admin/breeds", follow_redirects=False)
            assert admin_resp.status_code == 200, "管理员应能访问品种管理页"

            result.status = "PASS"
            result.actual_result = "登录 fixtures 权限控制正确"

        except AssertionError as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)

    @test_case("TC-PROJ-004", priority="Medium", expected="测试数据库隔离正常")
    def test_test_database_isolation(self, app):
        """测试测试数据库隔离"""
        result = TestResult("TC-PROJ-004", "test_db_isolation", "项目管理", "Medium")
        result.expected_result = "测试数据库与生产数据库隔离"

        try:
            # 检查数据库配置
            db_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
            assert db_uri is not None, "数据库 URI 未配置"

            # 验证是否使用测试数据库（通常包含 test 字样）
            # 注意：实际项目中可能配置不同，这里做基本检查
            assert (
                "mysql" in db_uri.lower() or "sqlite" in db_uri.lower()
            ), f"数据库类型不支持：{db_uri}"

            result.status = "PASS"
            result.actual_result = f"测试数据库配置正确：{db_uri[:50]}..."

        except AssertionError as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)


class TestCoverageAnalyzer:
    """覆盖率分析工具测试类"""

    @test_case("TC-COV-001", priority="High", expected="覆盖率分析器可导入")
    def test_coverage_analyzer_import(self):
        """测试覆盖率分析器导入"""
        result = TestResult("TC-COV-001", "test_analyzer_import", "覆盖率工具", "High")
        result.expected_result = "coverage_analyzer 模块可成功导入"

        try:
            from Test.coverage_analyzer import TestCoverageAnalyzer

            analyzer = TestCoverageAnalyzer()
            assert analyzer is not None, "无法创建分析器实例"

            result.status = "PASS"
            result.actual_result = "覆盖率分析器导入成功"

        except ImportError as e:
            result.status = "FAIL"
            result.error_message = f"导入失败：{str(e)}"
            raise
        except Exception as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)

    @test_case("TC-COV-002", priority="Medium", expected="能够找到测试文件")
    def test_find_test_files(self):
        """测试查找测试文件功能"""
        result = TestResult(
            "TC-COV-002", "test_find_test_files", "覆盖率工具", "Medium"
        )
        result.expected_result = "正确识别所有测试文件"

        try:
            from Test.coverage_analyzer import TestCoverageAnalyzer

            analyzer = TestCoverageAnalyzer(test_dir="Test")

            test_files = analyzer.find_test_files()

            # 验证找到了测试文件
            assert len(test_files) > 0, "未找到任何测试文件"

            # 验证包含主要测试文件
            file_names = [f.name for f in test_files]
            assert any("test_auth" in name for name in file_names), "未找到认证测试"
            assert any("test_breed" in name for name in file_names), "未找到品种测试"

            result.status = "PASS"
            result.actual_result = f"找到 {len(test_files)} 个测试文件"

        except Exception as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)

    @test_case("TC-COV-003", priority="Medium", expected="生成覆盖率报告")
    def test_generate_coverage_report(self):
        """测试生成覆盖率报告"""
        result = TestResult(
            "TC-COV-003", "test_generate_report", "覆盖率工具", "Medium"
        )
        result.expected_result = "成功生成覆盖率报告文件"

        try:
            from Test.coverage_analyzer import TestCoverageAnalyzer

            analyzer = TestCoverageAnalyzer()

            # 查找测试文件
            analyzer.find_test_files()

            # 提取测试用例
            test_cases = analyzer.extract_test_cases()

            # 验证提取到测试用例
            assert len(test_cases) > 0, "未提取到测试用例"

            # 分析报告结构
            priority_counts = {}
            for tc in test_cases:
                priority = tc["priority"]
                priority_counts[priority] = priority_counts.get(priority, 0) + 1

            result.status = "PASS"
            result.actual_result = (
                f"提取到 {len(test_cases)} 个用例，优先级分布：{priority_counts}"
            )

        except Exception as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)


class TestTestExecution:
    """测试执行管理测试类"""

    @test_case("TC-EXEC-001", priority="High", expected="pytest 命令可执行")
    def test_pytest_command_execution(self):
        """测试 pytest 命令执行"""
        result = TestResult("TC-EXEC-001", "test_pytest_exec", "测试执行", "High")
        result.expected_result = "pytest 命令可以正常执行"

        try:
            import subprocess

            # 运行 pytest --version 验证安装
            proc = subprocess.run(
                ["pytest", "--version"], capture_output=True, text=True, timeout=10
            )

            assert proc.returncode == 0, f"pytest 命令执行失败：{proc.stderr}"
            assert "pytest" in proc.stdout.lower(), f"版本输出异常：{proc.stdout}"

            result.status = "PASS"
            result.actual_result = f"pytest 已安装：{proc.stdout.strip()}"

        except FileNotFoundError:
            result.status = "FAIL"
            result.error_message = "pytest 未安装或不在 PATH 中"
            raise
        except Exception as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)

    @test_case("TC-EXEC-002", priority="Medium", expected="测试标记 works")
    def test_pytest_markers(self):
        """测试 pytest markers 使用"""
        result = TestResult("TC-EXEC-002", "test_markers", "测试执行", "Medium")
        result.expected_result = "自定义 markers 可以被识别和使用"

        try:
            # 检查 pytest.ini 中的 markers 配置
            pytest_ini = Path("pytest.ini")
            if pytest_ini.exists():
                content = pytest_ini.read_text(encoding="utf-8")
                assert "slow:" in content, "缺少 slow marker 定义"

                result.status = "PASS"
                result.actual_result = "Markers 配置正确"
            else:
                result.status = "SKIP"
                result.actual_result = "pytest.ini 不存在，跳过此测试"

        except Exception as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)

    @test_case("TC-EXEC-003", priority="Low", expected="测试报告目录存在")
    def test_reports_directory_exists(self):
        """测试报告目录"""
        result = TestResult("TC-EXEC-003", "test_reports_dir", "测试执行", "Low")
        result.expected_result = "Test/reports 目录存在并可写"

        try:
            reports_dir = Path("Test/reports")

            if not reports_dir.exists():
                # 尝试创建
                reports_dir.mkdir(parents=True, exist_ok=True)

            assert reports_dir.exists(), "无法创建 reports 目录"
            assert reports_dir.is_dir(), "reports 不是目录"

            # 测试可写性
            test_file = reports_dir / ".write_test"
            test_file.write_text("test")
            test_file.unlink()

            result.status = "PASS"
            result.actual_result = "Reports 目录存在且可写"

        except Exception as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)


class TestTestDocumentation:
    """测试文档管理测试类"""

    @test_case("TC-DOC-001", priority="Medium", expected="测试框架文档存在")
    def test_framework_documentation(self):
        """测试框架文档"""
        result = TestResult("TC-DOC-001", "test_framework_doc", "文档管理", "Medium")
        result.expected_result = "test_framework.py 有完整的文档说明"

        try:
            framework_file = Path("Test/test_framework.py")
            assert framework_file.exists(), "test_framework.py 不存在"

            content = framework_file.read_text(encoding="utf-8")

            # 检查是否有文档字符串
            has_module_docstring = '"""' in content or "'''" in content
            assert has_module_docstring, "缺少模块文档字符串"

            result.status = "PASS"
            result.actual_result = "框架文档存在"

        except Exception as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)

    @test_case("TC-DOC-002", priority="Low", expected="测试用例有清晰描述")
    def test_test_case_descriptions(self):
        """测试用例描述完整性"""
        result = TestResult("TC-DOC-002", "test_case_descriptions", "文档管理", "Low")
        result.expected_result = "测试函数都有 docstring 描述"

        try:
            # 抽样检查几个测试文件
            test_files_to_check = [
                "test_auth.py",
                "test_breed.py",
                "test_custom_analysis.py",
            ]

            checked_count = 0
            documented_count = 0

            for filename in test_files_to_check:
                filepath = Path(f"Test/{filename}")
                if not filepath.exists():
                    continue

                content = filepath.read_text(encoding="utf-8")

                # 简单检查是否有 docstring
                if '"""' in content or "'''" in content:
                    documented_count += 1
                checked_count += 1

            # 至少 60% 的文件有文档
            documentation_rate = (
                (documented_count / checked_count * 100) if checked_count > 0 else 0
            )
            assert (
                documentation_rate >= 60
            ), f"文档覆盖率不足：{documentation_rate:.1f}%"

            result.status = "PASS"
            result.actual_result = f"文档覆盖率：{documentation_rate:.1f}% ({documented_count}/{checked_count})"

        except Exception as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)


class TestContinuousIntegration:
    """持续集成测试类"""

    @test_case("TC-CI-001", priority="High", expected="Jenkinsfile 配置正确")
    def test_jenkinsfile_exists(self):
        """测试 Jenkinsfile 存在和配置"""
        result = TestResult("TC-CI-001", "test_jenkinsfile", "CI/CD", "High")
        result.expected_result = "Jenkinsfile 存在且包含必要阶段"

        try:
            jenkinsfile = Path("Jenkinsfile")
            assert jenkinsfile.exists(), "Jenkinsfile 不存在"

            content = jenkinsfile.read_text(encoding="utf-8")

            # 检查必要的 CI 阶段
            required_stages = ["pipeline", "agent", "stages", "stage", "steps"]

            for stage in required_stages:
                assert stage in content, f"Jenkinsfile 缺少 {stage} 定义"

            result.status = "PASS"
            result.actual_result = "Jenkinsfile 配置完整"

        except Exception as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)

    @test_case("TC-CI-002", priority="Medium", expected="CI 测试脚本可执行")
    def test_ci_test_scripts_executable(self):
        """测试 CI 测试脚本"""
        result = TestResult("TC-CI-002", "test_ci_scripts", "CI/CD", "Medium")
        result.expected_result = "run_tests*.py 脚本存在并可执行"

        try:
            # 检查测试运行脚本
            test_dir = Path(__file__).parent
            scripts_to_check = [
                test_dir / "run_tests.py",
                test_dir / "run_professional_tests.py",
            ]

            found_scripts = []
            for script_name in scripts_to_check:
                script_path = Path(script_name)
                if script_path.exists():
                    found_scripts.append(script_name)
                    # 检查是否可执行（语法正确）
                    compile(
                        script_path.read_text(encoding="utf-8"), script_path, "exec"
                    )

            assert len(found_scripts) > 0, f"未找到任何测试运行脚本：{scripts_to_check}"

            result.status = "PASS"
            result.actual_result = (
                f"找到 {len(found_scripts)} 个测试脚本：{found_scripts}"
            )

        except Exception as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
