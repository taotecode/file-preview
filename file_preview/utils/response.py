"""
响应工具函数
"""

from flask import jsonify

def generate_error_response(error_message, status_code=400):
    """
    生成标准错误响应
    
    Args:
        error_message: 错误信息
        status_code: HTTP状态码
        
    Returns:
        元组 (响应JSON, 状态码)
    """
    return jsonify({
        'status': 'failed',
        'message': error_message,
        'error': error_message
    }), status_code 