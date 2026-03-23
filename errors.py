"""
统一错误处理模块
提供友好的错误响应，避免泄露敏感信息
"""
from flask import jsonify, render_template
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        if request.is_json:
            return jsonify({'error': '请求参数错误', 'message': str(error)}), 400
        return render_template('error.html', error=error), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        if request.is_json:
            return jsonify({'error': '未授权', 'message': '请先登录'}), 401
        flash('请先登录', 'warning')
        return redirect(url_for('login'))
    
    @app.errorhandler(403)
    def forbidden(error):
        if request.is_json:
            return jsonify({'error': '禁止访问', 'message': '权限不足'}), 403
        return render_template('error.html', error=error), 403
    
    @app.errorhandler(404)
    def not_found(error):
        if request.is_json:
            return jsonify({'error': '资源不存在'}), 404
        return render_template('error.html', error=error), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        if request.is_json:
            return jsonify({'error': '方法不允许'}), 405
        return render_template('error.html', error=error), 405
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        if request.is_json:
            return jsonify({'error': '请求数据无法处理'}), 422
        return render_template('error.html', error=error), 422
    
    @app.errorhandler(500)
    def internal_server_error(error):
        # 记录错误日志（后续添加日志系统）
        app.logger.error(f'服务器内部错误：{str(error)}')
        
        if request.is_json:
            return jsonify({'error': '服务器内部错误', 'message': '请稍后重试'}), 500
        return render_template('error.html', error=error), 500
    
    # 捕获所有未处理的异常
    @app.errorhandler(Exception)
    def handle_exception(error):
        # 记录错误日志
        app.logger.error(f'未处理的异常：{str(error)}', exc_info=True)
        
        if request.is_json:
            return jsonify({'error': '服务异常', 'message': '请稍后重试'}), 500
        
        # 如果是 HTTP 异常，交给对应的处理器
        if isinstance(error, HTTPException):
            raise error
        
        return render_template('error.html', error=error), 500


# 导入时需要的依赖
from flask import request, url_for, flash, redirect
