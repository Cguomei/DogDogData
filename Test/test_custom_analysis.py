"""
自定义数据分析模块测试用例
覆盖文件上传、数据解析、图表生成等功能
"""
import pytest
import io
from test_framework import test_case, test_manager, TestResult


class TestCustomAnalysis:
    """自定义数据分析测试类"""
    
    @test_case('TC-ANALYSIS-001', priority='High', expected='成功上传 CSV 文件')
    def test_upload_csv_file(self, logged_in_client):
        """上传 CSV 文件"""
        result = TestResult('TC-ANALYSIS-001', 'test_upload_csv', '自定义分析', 'High')
        result.expected_result = '成功解析 CSV 文件并返回数据'
        
        try:
            # 创建测试 CSV 文件
            csv_content = b"""品种，数量，价格
哈士奇，50,3000
泰迪，80,2500
金毛，60,3500"""
            
            data = {'file': (io.BytesIO(csv_content), 'test_data.csv')}
            response = logged_in_client.post(
                '/api/upload-data',
                data=data,
                content_type='multipart/form-data'
            )
            
            assert response.status_code == 200
            json_data = response.get_json()
            assert json_data['success'] == True
            assert 'columns' in json_data
            assert 'row_count' in json_data
            assert json_data['row_count'] == 3
            
            result.status = 'PASS'
            result.actual_result = f"成功上传 CSV，{json_data['row_count']}行数据"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-ANALYSIS-002', priority='High', expected='成功上传 Excel 文件')
    def test_upload_excel_file(self, logged_in_client):
        """上传 Excel 文件"""
        result = TestResult('TC-ANALYSIS-002', 'test_upload_excel', '自定义分析', 'High')
        result.expected_result = '成功解析 Excel 文件'
        
        try:
            # 需要有实际的 Excel 文件用于测试
            # 这里使用 CSV 模拟（实际应该用 openpyxl 创建 Excel）
            pytest.skip("需要实际的 Excel 文件支持")
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-ANALYSIS-003', priority='Medium', expected='拒绝不支持的文件格式')
    def test_upload_unsupported_format(self, logged_in_client):
        """上传不支持的文件格式"""
        result = TestResult('TC-ANALYSIS-003', 'test_unsupported_format', '自定义分析', 'Medium')
        result.expected_result = '拒绝.txt 等不支持的格式'
        
        try:
            # 创建 txt 文件
            txt_content = b"This is a text file"
            data = {'file': (io.BytesIO(txt_content), 'test.txt')}
            response = logged_in_client.post(
                '/api/upload-data',
                data=data,
                content_type='multipart/form-data'
            )
            
            assert response.status_code == 400
            json_data = response.get_json()
            assert 'error' in json_data
            
            result.status = 'PASS'
            result.actual_result = "正确拒绝不支持的文件格式"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-ANALYSIS-004', priority='Medium', expected='生成图表成功')
    def test_generate_chart(self, logged_in_client):
        """生成自定义图表"""
        result = TestResult('TC-ANALYSIS-004', 'test_generate_chart', '自定义分析', 'Medium')
        result.expected_result = '根据配置生成图表'
        
        try:
            chart_config = {
                'chart_type': 'bar',
                'x_column': '品种',
                'y_column': '数量',
                'title': '品种数量统计'
            }
            
            response = logged_in_client.post(
                '/api/generate-chart',
                json=chart_config,
                content_type='application/json'
            )
            
            assert response.status_code == 200
            json_data = response.get_json()
            assert json_data['success'] == True
            
            result.status = 'PASS'
            result.actual_result = "图表生成成功"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-ANALYSIS-005', priority='Low', expected='访问自定义分析页面')
    def test_access_analysis_page(self, client):
        """访问自定义数据分析页面"""
        result = TestResult('TC-ANALYSIS-005', 'test_analysis_page', '自定义分析', 'Low')
        result.expected_result = '返回 HTML 页面'
        
        try:
            response = client.get('/custom-analysis')
            assert response.status_code == 200
            assert b'自定义数据分析' in response.data or b'上传数据' in response.data
            
            result.status = 'PASS'
            result.actual_result = "页面访问正常"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)


class TestDataValidation:
    """数据验证测试类"""
    
    @test_case('TC-VALIDATION-001', priority='Medium', expected='CSV 列名识别正确')
    def test_csv_column_detection(self, logged_in_client):
        """CSV 列名检测"""
        result = TestResult('TC-VALIDATION-001', 'test_csv_columns', '数据验证', 'Medium')
        result.expected_result = '正确识别 CSV 列名'
        
        try:
            csv_content = b"""name,age,price
test1,10,100
test2,20,200"""
            
            data = {'file': (io.BytesIO(csv_content), 'columns_test.csv')}
            response = logged_in_client.post(
                '/api/upload-data',
                data=data,
                content_type='multipart/form-data'
            )
            
            assert response.status_code == 200
            json_data = response.get_json()
            columns = json_data['columns']
            assert 'name' in columns
            assert 'age' in columns
            assert 'price' in columns
            
            result.status = 'PASS'
            result.actual_result = f"列名识别正确：{columns}"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-VALIDATION-002', priority='Medium', expected='空文件处理正确')
    def test_empty_file_handling(self, logged_in_client):
        """上传空文件"""
        result = TestResult('TC-VALIDATION-002', 'test_empty_file', '数据验证', 'Medium')
        result.expected_result = '拒绝空文件或提示无数据'
        
        try:
            # 空 CSV 文件
            csv_content = b""
            data = {'file': (io.BytesIO(csv_content), 'empty.csv')}
            response = logged_in_client.post(
                '/api/upload-data',
                data=data,
                content_type='multipart/form-data'
            )
            
            # 应该返回错误或空数据
            assert response.status_code in [200, 400]
            
            result.status = 'PASS'
            result.actual_result = "空文件处理正常"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
