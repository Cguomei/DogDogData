"""
API 响应工具类
统一 API 响应格式，便于前端处理和 APP 调用
"""
from flask import jsonify, make_response
from functools import wraps


class APIResponse:
    """API 响应助手"""
    
    @staticmethod
    def success(data=None, message='操作成功', code=200, **kwargs):
        """
        成功响应
        
        Args:
            data: 返回的数据
            message: 成功消息
            code: HTTP 状态码
            kwargs: 额外的元数据
            
        Returns:
            JSON 响应
        """
        response = {
            'code': code,
            'success': True,
            'message': message,
            'data': data,
            'timestamp': int(time.time())
        }
        
        # 添加额外元数据
        if kwargs:
            response['meta'] = kwargs
            
        return jsonify(response), code
    
    @staticmethod
    def error(message='操作失败', code=400, error_code=None, data=None):
        """
        错误响应
        
        Args:
            message: 错误消息
            code: HTTP 状态码
            error_code: 业务错误码（为 APP 预留）
            data: 附加数据
            
        Returns:
            JSON 响应
        """
        response = {
            'code': code,
            'success': False,
            'message': message,
            'data': data,
            'timestamp': int(time.time())
        }
        
        # 添加业务错误码（为 APP 预留）
        if error_code is not None:
            response['error_code'] = error_code
            
        return jsonify(response), code
    
    @staticmethod
    def created(data=None, message='创建成功'):
        """创建成功响应 (201)"""
        return APIResponse.success(data, message, code=201)
    
    @staticmethod
    def no_content():
        """无内容响应 (204)"""
        return '', 204
    
    @staticmethod
    def unauthorized(message='未授权，请先登录'):
        """未授权响应 (401)"""
        return APIResponse.error(message, code=401, error_code='UNAUTHORIZED')
    
    @staticmethod
    def forbidden(message='权限不足'):
        """禁止访问响应 (403)"""
        return APIResponse.error(message, code=403, error_code='FORBIDDEN')
    
    @staticmethod
    def not_found(message='资源不存在'):
        """资源不存在响应 (404)"""
        return APIResponse.error(message, code=404, error_code='NOT_FOUND')
    
    @staticmethod
    def validation_error(errors, message='参数验证失败'):
        """
        参数验证错误响应
        
        Args:
            errors: 验证错误列表
            message: 错误消息
        """
        return APIResponse.error(
            message=message,
            code=400,
            error_code='VALIDATION_ERROR',
            data={'errors': errors}
        )
    
    @staticmethod
    def paginate(data, total, page, per_page, message='获取成功'):
        """
        分页响应
        
        Args:
            data: 数据列表
            total: 总数
            page: 当前页码
            per_page: 每页数量
            message: 消息
        """
        meta = {
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
            'has_next': page * per_page < total,
            'has_prev': page > 1
        }
        
        return APIResponse.success(data, message, **meta)


# 装饰器
def api_response(func):
    """
    API 响应装饰器
    自动将返回值包装为标准 API 响应格式
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # 如果已经是元组（response, status_code），直接返回
            if isinstance(result, tuple):
                return result
            
            # 如果是字典，包装成成功响应
            if isinstance(result, dict):
                return APIResponse.success(result)
            
            return result
        except Exception as e:
            # 异常时返回错误响应
            return APIResponse.error(str(e), code=500)
    
    return wrapper


# 需要导入的模块
import time
