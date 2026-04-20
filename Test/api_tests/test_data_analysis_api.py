"""
自定义数据分析 API 测试
涵盖：数据上传、质量校验、图表生成、数据导出
"""
import pytest
import io
import pandas as pd


class TestDataUpload:
    """数据上传 API 测试"""
    
    def test_upload_csv_file(self, api_client, validator):
        """测试 1: 上传 CSV 文件"""
        # 创建测试 CSV 数据
        csv_data = """年龄,体重,品种
3,15.5,金毛
5,20.3,哈士奇
2,8.7,柯基"""
        
        data = {
            'file': (io.BytesIO(csv_data.encode('utf-8')), 'test_data.csv')
        }
        
        response = api_client.post('/api/upload-data', 
                                   data=data, 
                                   content_type='multipart/form-data')
        validator.assert_success(response)
        
        result = response.get_json()
        assert result['success'] is True
        assert 'columns' in result
        assert 'data' in result
        assert 'quality_report' in result
        
        print(f"✅ 测试 1 通过：CSV 上传成功，{result['row_count']} 行数据")
    
    def test_upload_excel_file(self, api_client, validator):
        """测试 2: 上传 Excel 文件"""
        # 创建测试 DataFrame
        df = pd.DataFrame({
            '年龄': [3, 5, 2],
            '体重': [15.5, 20.3, 8.7],
            '品种': ['金毛', '哈士奇', '柯基']
        })
        
        # 转换为 Excel 字节流
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        excel_buffer.seek(0)
        
        data = {
            'file': (excel_buffer, 'test_data.xlsx')
        }
        
        response = api_client.post('/api/upload-data',
                                   data=data,
                                   content_type='multipart/form-data')
        validator.assert_success(response)
        
        result = response.get_json()
        assert result['success'] is True
        assert result['row_count'] == 3
        
        print(f"✅ 测试 2 通过：Excel 上传成功，{result['row_count']} 行数据")
    
    def test_upload_without_file(self, api_client, validator):
        """测试 3: 未上传文件（应返回错误）"""
        response = api_client.post('/api/upload-data', data={})
        validator.assert_error(response, expected_status=400)
        
        result = response.get_json()
        assert 'error' in result
        
        print("✅ 测试 3 通过：未上传文件返回错误提示")
    
    def test_upload_invalid_format(self, api_client, validator):
        """测试 4: 上传不支持的文件格式"""
        data = {
            'file': (io.BytesIO(b'test'), 'test.txt')
        }
        
        response = api_client.post('/api/upload-data',
                                   data=data,
                                   content_type='multipart/form-data')
        validator.assert_error(response, expected_status=400)
        
        print("✅ 测试 4 通过：不支持的文件格式被拒绝")
    
    def test_data_quality_validation(self, api_client, validator):
        """测试 5: 数据质量校验"""
        # 创建包含问题的测试数据
        csv_data = """年龄,体重,品种
3,15.5,金毛
,-20.3,哈士奇
2,,柯基
3,15.5,金毛"""  # 包含空值、负数、重复行
        
        data = {
            'file': (io.BytesIO(csv_data.encode('utf-8')), 'quality_test.csv')
        }
        
        response = api_client.post('/api/upload-data',
                                   data=data,
                                   content_type='multipart/form-data')
        validator.assert_success(response)
        
        result = response.get_json()
        quality_report = result['quality_report']
        
        # 验证质量报告包含问题检测
        assert 'issues' in quality_report
        assert len(quality_report['issues']) > 0, "应检测到数据质量问题"
        
        print(f"✅ 测试 5 通过：检测到 {len(quality_report['issues'])} 个数据质量问题")
        for issue in quality_report['issues']:
            print(f"   - {issue['message']}")


class TestChartGeneration:
    """图表生成 API 测试"""
    
    def test_generate_scatter_chart(self, api_client, validator):
        """测试 6: 生成散点图"""
        chart_config = {
            'chart_type': 'scatter',
            'x_column': '年龄',
            'y_column': '体重',
            'title': '年龄-体重散点图',
            'data': [
                {'年龄': 3, '体重': 15.5},
                {'年龄': 5, '体重': 20.3},
                {'年龄': 2, '体重': 8.7}
            ]
        }
        
        response = api_client.post('/api/generate-chart', json=chart_config)
        validator.assert_success(response)
        
        result = response.get_json()
        validator.validate_chart_response(result)
        assert result['data_points'] == 3
        
        print(f"✅ 测试 6 通过：散点图生成成功，{result['data_points']} 个数据点")
    
    def test_generate_line_chart(self, api_client, validator):
        """测试 7: 生成折线图"""
        chart_config = {
            'chart_type': 'line',
            'x_column': '月份',
            'y_column': '销量',
            'title': '月度销售趋势',
            'data': [
                {'月份': 1, '销量': 100},
                {'月份': 2, '销量': 150},
                {'月份': 3, '销量': 120}
            ]
        }
        
        response = api_client.post('/api/generate-chart', json=chart_config)
        validator.assert_success(response)
        
        result = response.get_json()
        validator.validate_chart_response(result)
        
        print("✅ 测试 7 通过：折线图生成成功")
    
    def test_generate_bar_chart(self, api_client, validator):
        """测试 8: 生成柱状图"""
        chart_config = {
            'chart_type': 'bar',
            'x_column': '品种',
            'y_column': '数量',
            'title': '各品种数量统计',
            'data': [
                {'品种': '金毛', '数量': 50},
                {'品种': '哈士奇', '数量': 30},
                {'品种': '柯基', '数量': 20}
            ]
        }
        
        response = api_client.post('/api/generate-chart', json=chart_config)
        validator.assert_success(response)
        
        result = response.get_json()
        validator.validate_chart_response(result)
        
        print("✅ 测试 8 通过：柱状图生成成功")
    
    def test_generate_pie_chart(self, api_client, validator):
        """测试 9: 生成饼图"""
        chart_config = {
            'chart_type': 'pie',
            'x_column': '类别',
            'y_column': '占比',
            'title': '数据分布',
            'data': [
                {'类别': 'A', '占比': 40},
                {'类别': 'B', '占比': 35},
                {'类别': 'C', '占比': 25}
            ]
        }
        
        response = api_client.post('/api/generate-chart', json=chart_config)
        validator.assert_success(response)
        
        result = response.get_json()
        validator.validate_chart_response(result)
        
        print("✅ 测试 9 通过：饼图生成成功")
    
    def test_generate_chart_missing_params(self, api_client, validator):
        """测试 10: 缺少必要参数（应返回错误）"""
        invalid_config = {
            'chart_type': 'scatter',
            # 缺少 x_column 和 y_column
            'data': [{'x': 1, 'y': 2}]
        }
        
        response = api_client.post('/api/generate-chart', json=invalid_config)
        validator.assert_error(response, expected_status=400)
        
        print("✅ 测试 10 通过：缺少参数返回错误提示")
    
    def test_generate_chart_invalid_columns(self, api_client, validator):
        """测试 11: 列名不存在（应返回错误）"""
        chart_config = {
            'chart_type': 'scatter',
            'x_column': '不存在的列',
            'y_column': '体重',
            'data': [{'年龄': 3, '体重': 15.5}]
        }
        
        response = api_client.post('/api/generate-chart', json=chart_config)
        validator.assert_error(response, expected_status=400)
        
        print("✅ 测试 11 通过：无效列名返回错误提示")
    
    def test_generate_chart_empty_data(self, api_client, validator):
        """测试 12: 空数据（应返回错误）"""
        chart_config = {
            'chart_type': 'scatter',
            'x_column': '年龄',
            'y_column': '体重',
            'data': []
        }
        
        response = api_client.post('/api/generate-chart', json=chart_config)
        validator.assert_error(response, expected_status=400)
        
        print("✅ 测试 12 通过：空数据返回错误提示")


class TestDataExport:
    """数据导出 API 测试"""
    
    def test_export_to_csv(self, api_client, validator):
        """测试 13: 导出数据为 CSV"""
        export_data = {
            'format': 'csv',
            'filename': 'test_export',
            'data': [
                {'姓名': '张三', '年龄': 25},
                {'姓名': '李四', '年龄': 30}
            ]
        }
        
        response = api_client.post('/api/export-data', json=export_data)
        validator.assert_success(response)
        
        # 验证响应头
        assert 'text/csv' in response.content_type
        
        print("✅ 测试 13 通过：CSV 导出成功")
    
    def test_export_to_excel(self, api_client, validator):
        """测试 14: 导出数据为 Excel"""
        export_data = {
            'format': 'excel',
            'filename': 'test_export',
            'data': [
                {'姓名': '张三', '年龄': 25},
                {'姓名': '李四', '年龄': 30}
            ]
        }
        
        response = api_client.post('/api/export-data', json=export_data)
        validator.assert_success(response)
        
        # 验证响应头
        assert 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in response.content_type
        
        print("✅ 测试 14 通过：Excel 导出成功")
    
    def test_export_empty_data(self, api_client, validator):
        """测试 15: 导出空数据（应返回错误）"""
        export_data = {
            'format': 'csv',
            'filename': 'test_export',
            'data': []
        }
        
        response = api_client.post('/api/export-data', json=export_data)
        validator.assert_error(response, expected_status=400)
        
        print("✅ 测试 15 通过：空数据导出返回错误提示")


# 运行测试
if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s",
        "--html=Test/reports/api_data_analysis_test_report.html",
        "--self-contained-html"
    ])
