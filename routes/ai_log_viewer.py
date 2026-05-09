"""
AI助手日志查看工具
实时显示最近的日志和错误
"""
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
import os
from datetime import datetime

log_viewer_bp = Blueprint('log_viewer', __name__)

LOG_FILE = 'log/ai_assistant.log'


@log_viewer_bp.route('/ai-logs')
@login_required
def logs_page():
    """日志查看页面（仅管理员）"""
    if not current_user.is_admin():
        return '权限不足', 403
    return render_template('ai_logs.html')


@log_viewer_bp.route('/api/ai/logs/recent')
@login_required
def get_recent_logs():
    """获取最近的日志（仅管理员）"""
    if not current_user.is_admin():
        return jsonify({'error': '权限不足'}), 403
    
    try:
        lines_count = request.args.get('lines', 100, type=int)
        
        if not os.path.exists(LOG_FILE):
            return jsonify({
                'success': True,
                'logs': [],
                'message': '日志文件不存在'
            })
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_lines = lines[-lines_count:]
        
        # 解析日志
        logs = []
        for line in recent_lines:
            line = line.strip()
            if not line:
                continue
            
            # 简单的日志解析
            log_entry = {
                'raw': line,
                'timestamp': None,
                'level': None,
                'message': None
            }
            
            # 尝试提取时间戳和级别
            try:
                parts = line.split(' - ', 3)
                if len(parts) >= 4:
                    log_entry['timestamp'] = parts[0]
                    log_entry['level'] = parts[2]
                    log_entry['message'] = parts[3]
            except:
                pass
            
            logs.append(log_entry)
        
        # 统计信息
        error_count = sum(1 for log in logs if log['level'] == 'ERROR')
        warning_count = sum(1 for log in logs if log['level'] == 'WARNING')
        
        return jsonify({
            'success': True,
            'logs': logs,
            'total_lines': len(lines),
            'returned_lines': len(logs),
            'error_count': error_count,
            'warning_count': warning_count,
            'file_size': os.path.getsize(LOG_FILE) if os.path.exists(LOG_FILE) else 0
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@log_viewer_bp.route('/api/ai/logs/errors')
@login_required
def get_recent_errors():
    """获取最近的错误日志（仅管理员）"""
    if not current_user.is_admin():
        return jsonify({'error': '权限不足'}), 403
    
    try:
        if not os.path.exists(LOG_FILE):
            return jsonify({
                'success': True,
                'errors': []
            })
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 只提取ERROR级别的日志
        errors = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if 'ERROR' in line:
                error_entry = {
                    'timestamp': None,
                    'message': line,
                    'traceback': []
                }
                
                # 提取时间戳
                try:
                    parts = line.split(' - ', 1)
                    if len(parts) >= 1:
                        error_entry['timestamp'] = parts[0]
                except:
                    pass
                
                # 收集后续的堆栈跟踪
                i += 1
                while i < len(lines) and (lines[i].startswith(' ') or lines[i].startswith('Traceback') or 'File "' in lines[i]):
                    error_entry['traceback'].append(lines[i].strip())
                    i += 1
                
                errors.append(error_entry)
            else:
                i += 1
        
        # 只返回最近的50个错误
        recent_errors = errors[-50:]
        
        return jsonify({
            'success': True,
            'errors': recent_errors,
            'total_errors': len(errors)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@log_viewer_bp.route('/api/ai/logs/clear', methods=['POST'])
@login_required
def clear_logs():
    """清空日志文件（仅管理员）"""
    if not current_user.is_admin():
        return jsonify({'error': '权限不足'}), 403
    
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                f.write('')
            return jsonify({
                'success': True,
                'message': '日志已清空'
            })
        else:
            return jsonify({
                'success': True,
                'message': '日志文件不存在'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
