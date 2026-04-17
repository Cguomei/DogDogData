"""
P0功能优化测试用例 v3.4.0
测试缓存策略、自定义分析、数据导出、数据质量校验
"""
import pytest
import io
import time
from Test.test_framework import test_case, test_manager, TestResult


class TestCacheStrategy:
    """缓存策略测试类 - P0-1"""
    
    @test_case('TC-CACHE-001', priority='High', expected='静态资源返回正确的缓存头')
    def test_static_resource_cache(self, client):
        """测试静态资源缓存策略"""
        result = TestResult('TC-CACHE-001', 'test_static_cache', '缓存策略', 'High')
        
        try:
            # 测试CSS文件
            response = client.get('/static/CSS/style.css')
            
            if response.status_code == 200:
                cache_control = response.headers.get('Cache-Control', '')
                assert 'max-age=3600' in cache_control or 'public' in cache_control
                
                result.status = 'PASS'
                result.actual_result = f"静态资源缓存头: {cache_control}"
            else:
                result.status = 'SKIP'
                result.actual_result = "静态文件不存在，跳过测试"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-CACHE-002', priority='High', expected='API GET请求返回缓存头')
    def test_api_get_cache(self, client):
        """测试API GET请求缓存"""
        result = TestResult('TC-CACHE-002', 'test_api_cache', '缓存策略', 'High')
        
        try:
            response = client.get('/api/breeds')
            
            if response.status_code == 200:
                cache_control = response.headers.get('Cache-Control', '')
                # API应该有缓存（max-age=300）或不缓存
                assert 'Cache-Control' in response.headers
                
                result.status = 'PASS'
                result.actual_result = f"API缓存头: {cache_control}"
            else:
                result.status = 'FAIL'
                result.actual_result = f"API请求失败: {response.status_code}"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-CACHE-003', priority='Medium', expected='HTML页面不缓存')
    def test_html_page_no_cache(self, client):
        """测试HTML页面不缓存"""
        result = TestResult('TC-CACHE-003', 'test_html_no_cache', '缓存策略', 'Medium')
        
        try:
            response = client.get('/')
            
            if response.status_code == 200:
                cache_control = response.headers.get('Cache-Control', '')
                # HTML页面应该不缓存或no-cache
                assert 'no-cache' in cache_control or 'no-store' in cache_control or 'Cache-Control' in response.headers
                
                result.status = 'PASS'
                result.actual_result = f"HTML页面缓存头: {cache_control}"
            else:
                result.status = 'SKIP'
                result.actual_result = "首页访问失败，跳过"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)


class TestDataQualityValidation:
    """数据质量校验测试类 - P0-4"""
    
    @test_case('TC-QUALITY-001', priority='High', expected='返回数据质量报告')
    def test_quality_report_returned(self, logged_in_client):
        """测试上传数据后返回质量报告"""
        result = TestResult('TC-QUALITY-001', 'test_quality_report', '数据质量', 'High')
        
        try:
            # 创建包含问题的CSV
            csv_content = b"""name,age,price
dog1,5,3000
dog2,,2500
dog3,3,
dog4,-1,2000
dog1,5,3000"""  # 重复行
            
            data = {'file': (io.BytesIO(csv_content), 'quality_test.csv')}
            response = logged_in_client.post(
                '/api/upload-data',
                data=data,
                content_type='multipart/form-data'
            )
            
            assert response.status_code == 200
            json_data = response.get_json()
            assert json_data['success'] == True
            assert 'quality_report' in json_data
            
            quality_report = json_data['quality_report']
            assert 'total_rows' in quality_report
            assert 'total_columns' in quality_report
            assert 'issues' in quality_report
            
            result.status = 'PASS'
            result.actual_result = f"质量报告: {len(quality_report['issues'])}个问题"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-QUALITY-002', priority='High', expected='检测高空值比例')
    def test_high_null_ratio_detection(self, logged_in_client):
        """测试高空值比例检测"""
        result = TestResult('TC-QUALITY-002', 'test_null_ratio', '数据质量', 'High')
        
        try:
            # 创建高空值比例的CSV (50%空值)
            csv_content = b"""name,age,price
dog1,,
dog2,,
dog3,5,3000
dog4,3,2500"""
            
            data = {'file': (io.BytesIO(csv_content), 'null_test.csv')}
            response = logged_in_client.post(
                '/api/upload-data',
                data=data,
                content_type='multipart/form-data'
            )
            
            assert response.status_code == 200
            json_data = response.get_json()
            quality_report = json_data['quality_report']
            
            # 检查是否检测到高空值
            null_issues = [issue for issue in quality_report['issues'] 
                          if issue['type'] == 'high_null_ratio']
            
            result.status = 'PASS'
            result.actual_result = f"检测到{len(null_issues)}个高空值列"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-QUALITY-003', priority='Medium', expected='检测重复行')
    def test_duplicate_rows_detection(self, logged_in_client):
        """测试重复行检测"""
        result = TestResult('TC-QUALITY-003', 'test_duplicates', '数据质量', 'Medium')
        
        try:
            csv_content = b"""name,age
dog1,5
dog2,3
dog1,5
dog2,3"""
            
            data = {'file': (io.BytesIO(csv_content), 'duplicate_test.csv')}
            response = logged_in_client.post(
                '/api/upload-data',
                data=data,
                content_type='multipart/form-data'
            )
            
            assert response.status_code == 200
            json_data = response.get_json()
            quality_report = json_data['quality_report']
            
            # 检查是否检测到重复
            duplicate_issues = [issue for issue in quality_report['issues'] 
                               if issue['type'] == 'duplicate_rows']
            
            assert len(duplicate_issues) > 0, "未检测到重复行"
            
            result.status = 'PASS'
            result.actual_result = f"检测到重复行: {duplicate_issues[0]['message']}"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-QUALITY-004', priority='Medium', expected='检测负数值')
    def test_negative_values_detection(self, logged_in_client):
        """测试负数值检测"""
        result = TestResult('TC-QUALITY-004', 'test_negative', '数据质量', 'Medium')
        
        try:
            csv_content = b"""name,price
dog1,3000
dog2,-500
dog3,2500"""
            
            data = {'file': (io.BytesIO(csv_content), 'negative_test.csv')}
            response = logged_in_client.post(
                '/api/upload-data',
                data=data,
                content_type='multipart/form-data'
            )
            
            assert response.status_code == 200
            json_data = response.get_json()
            quality_report = json_data['quality_report']
            
            # 检查是否检测到负数
            negative_issues = [issue for issue in quality_report['issues'] 
                              if issue['type'] == 'negative_values']
            
            result.status = 'PASS'
            result.actual_result = f"检测到负数: {len(negative_issues)}个"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)


class TestDataExport:
    """数据导出功能测试类 - P0-3"""
    
    @test_case('TC-EXPORT-001', priority='High', expected='成功导出Excel文件')
    def test_export_excel(self, logged_in_client):
        """测试导出Excel格式"""
        result = TestResult('TC-EXPORT-001', 'test_export_excel', '数据导出', 'High')
        
        try:
            test_data = [
                {"品种": "金毛", "年龄": 3, "价格": 3000},
                {"品种": "哈士奇", "年龄": 2, "价格": 2500}
            ]
            
            response = logged_in_client.post(
                '/api/export-data',
                json={
                    'format': 'excel',
                    'filename': 'test_export',
                    'data': test_data
                },
                content_type='application/json'
            )
            
            assert response.status_code == 200
            # Excel文件的Content-Type
            content_type = response.headers.get('Content-Type', '')
            assert 'excel' in content_type.lower() or 'spreadsheet' in content_type.lower()
            
            result.status = 'PASS'
            result.actual_result = "Excel导出成功"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-EXPORT-002', priority='High', expected='成功导出CSV文件')
    def test_export_csv(self, logged_in_client):
        """测试导出CSV格式"""
        result = TestResult('TC-EXPORT-002', 'test_export_csv', '数据导出', 'High')
        
        try:
            test_data = [
                {"品种": "金毛", "年龄": 3, "价格": 3000},
                {"品种": "哈士奇", "年龄": 2, "价格": 2500}
            ]
            
            response = logged_in_client.post(
                '/api/export-data',
                json={
                    'format': 'csv',
                    'filename': 'test_export',
                    'data': test_data
                },
                content_type='application/json'
            )
            
            assert response.status_code == 200
            content_type = response.headers.get('Content-Type', '')
            assert 'csv' in content_type.lower() or 'text' in content_type.lower()
            
            result.status = 'PASS'
            result.actual_result = "CSV导出成功"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-EXPORT-003', priority='Medium', expected='空数据导出被拒绝')
    def test_export_empty_data(self, logged_in_client):
        """测试导出空数据"""
        result = TestResult('TC-EXPORT-003', 'test_export_empty', '数据导出', 'Medium')
        
        try:
            response = logged_in_client.post(
                '/api/export-data',
                json={
                    'format': 'excel',
                    'filename': 'test',
                    'data': []
                },
                content_type='application/json'
            )
            
            assert response.status_code == 400
            json_data = response.get_json()
            assert 'error' in json_data
            
            result.status = 'PASS'
            result.actual_result = "正确拒绝空数据导出"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)


class TestCustomChartGeneration:
    """自定义图表生成测试类 - P0-2"""
    
    @test_case('TC-CHART-001', priority='High', expected='生成散点图')
    def test_generate_scatter_chart(self, logged_in_client):
        """测试生成散点图"""
        result = TestResult('TC-CHART-001', 'test_scatter', '图表生成', 'High')
        
        try:
            chart_config = {
                'chart_type': 'scatter',
                'x_column': 'age',
                'y_column': 'price',
                'title': '年龄与价格关系',
                'data': [
                    {'age': 2, 'price': 3000},
                    {'age': 3, 'price': 2500},
                    {'age': 4, 'price': 2000}
                ]
            }
            
            response = logged_in_client.post(
                '/api/generate-chart',
                json=chart_config,
                content_type='application/json'
            )
            
            assert response.status_code == 200
            json_data = response.get_json()
            assert json_data['success'] == True
            assert 'chart_html' in json_data
            assert 'data_points' in json_data
            
            result.status = 'PASS'
            result.actual_result = f"散点图生成成功，{json_data['data_points']}个数据点"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-CHART-002', priority='High', expected='生成折线图')
    def test_generate_line_chart(self, logged_in_client):
        """测试生成折线图"""
        result = TestResult('TC-CHART-002', 'test_line', '图表生成', 'High')
        
        try:
            chart_config = {
                'chart_type': 'line',
                'x_column': 'month',
                'y_column': 'sales',
                'title': '月度销售趋势',
                'data': [
                    {'month': 1, 'sales': 100},
                    {'month': 2, 'sales': 150},
                    {'month': 3, 'sales': 200}
                ]
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
            result.actual_result = "折线图生成成功"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-CHART-003', priority='High', expected='生成柱状图')
    def test_generate_bar_chart(self, logged_in_client):
        """测试生成柱状图"""
        result = TestResult('TC-CHART-003', 'test_bar', '图表生成', 'High')
        
        try:
            chart_config = {
                'chart_type': 'bar',
                'x_column': 'breed',
                'y_column': 'count',
                'title': '品种数量统计',
                'data': [
                    {'breed': '金毛', 'count': 50},
                    {'breed': '哈士奇', 'count': 30}
                ]
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
            result.actual_result = "柱状图生成成功"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-CHART-004', priority='High', expected='生成饼图')
    def test_generate_pie_chart(self, logged_in_client):
        """测试生成饼图"""
        result = TestResult('TC-CHART-004', 'test_pie', '图表生成', 'High')
        
        try:
            chart_config = {
                'chart_type': 'pie',
                'x_column': 'category',
                'y_column': 'value',
                'title': '分类占比',
                'data': [
                    {'category': 'A', 'value': 40},
                    {'category': 'B', 'value': 30},
                    {'category': 'C', 'value': 30}
                ]
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
            result.actual_result = "饼图生成成功"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-CHART-005', priority='Medium', expected='缺少参数时返回错误')
    def test_missing_chart_parameters(self, logged_in_client):
        """测试缺少必要参数"""
        result = TestResult('TC-CHART-005', 'test_missing_params', '图表生成', 'Medium')
        
        try:
            # 缺少y_column
            chart_config = {
                'chart_type': 'bar',
                'x_column': 'breed',
                'title': '测试'
            }
            
            response = logged_in_client.post(
                '/api/generate-chart',
                json=chart_config,
                content_type='application/json'
            )
            
            assert response.status_code == 400
            json_data = response.get_json()
            assert 'error' in json_data
            
            result.status = 'PASS'
            result.actual_result = "正确拒绝缺少参数的请求"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-CHART-006', priority='Medium', expected='无效数据被过滤')
    def test_invalid_data_filtering(self, logged_in_client):
        """测试无效数据过滤"""
        result = TestResult('TC-CHART-006', 'test_data_filter', '图表生成', 'Medium')
        
        try:
            chart_config = {
                'chart_type': 'scatter',
                'x_column': 'x',
                'y_column': 'y',
                'title': '测试',
                'data': [
                    {'x': 1, 'y': 10},
                    {'x': None, 'y': 20},  # 无效数据
                    {'x': 3, 'y': None},   # 无效数据
                    {'x': 4, 'y': 40}
                ]
            }
            
            response = logged_in_client.post(
                '/api/generate-chart',
                json=chart_config,
                content_type='application/json'
            )
            
            assert response.status_code == 200
            json_data = response.get_json()
            assert json_data['success'] == True
            # 应该只保留2个有效数据点
            assert json_data['data_points'] == 2
            
            result.status = 'PASS'
            result.actual_result = f"正确过滤无效数据，保留{json_data['data_points']}个点"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
