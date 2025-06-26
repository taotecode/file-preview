"""
统计信息API
"""

from flask import request, jsonify, current_app
from file_preview.core.cache import CacheManager

def get_stats():
    """获取统计信息"""
    try:
        # 获取配置
        config = current_app.config['CONFIG']
        
        # 获取缓存管理器
        cache_manager = CacheManager(config)
        
        # 获取缓存统计信息
        stats = cache_manager.get_statistics()
        
        return jsonify({
            'status': 'success',
            'message': '获取统计信息成功',
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'status': 'failed',
            'message': '服务器内部错误',
            'error': str(e)
        }), 500 