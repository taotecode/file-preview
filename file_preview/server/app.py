"""
Flask应用创建和配置
"""

import os
import logging
from flask import Flask, jsonify
from .routes import api_bp, views_bp
from ..utils.config import load_config

def create_app(config_path=None):
    """
    创建Flask应用
    
    Args:
        config_path: 配置文件路径，默认None使用默认路径
        
    Returns:
        Flask应用实例
    """
    # 创建Flask应用
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    # 加载配置
    try:
        # 确保config_path是字符串或None
        if config_path is not None and not isinstance(config_path, (str, bytes, os.PathLike)):
            app.logger.warning(f"配置路径类型不正确: {type(config_path)}，将使用默认配置")
            config_path = None
            
        config = load_config(config_path)
        app.config['CONFIG'] = config
        
        # 配置日志
        log_dir = config.get('directories', {}).get('log', './logs')
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'app.log')),
                logging.StreamHandler()
            ]
        )
    except Exception as e:
        app.logger.error(f"加载配置失败: {str(e)}")
        # 使用默认配置
        app.config['CONFIG'] = {
            'server': {'host': '0.0.0.0', 'port': 5001},
            'directories': {
                'cache': './cache',
                'download': './download',
                'convert': './convert',
                'log': './logs'
            },
            'conversion': {
                'timeout': 60,
                'retry_times': 3,
                'libreoffice_path': 'libreoffice'
            }
        }
    
    # 注册蓝图
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)
    
    # 全局错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'failed',
            'message': '未找到',
            'error': str(error)
        }), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'status': 'failed',
            'message': '服务器错误',
            'error': str(error)
        }), 500
    
    return app 