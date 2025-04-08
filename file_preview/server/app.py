"""
Flask 应用
"""

import os
import logging
from flask import Flask
from ..utils.config import load_config
from ..utils.logger import setup_logger
from .routes import api_bp

def create_app() -> Flask:
    """
    创建 Flask 应用
    
    Returns:
        Flask 应用实例
    """
    # 创建应用
    app = Flask(__name__)
    
    # 加载配置
    config = load_config()
    
    # 设置日志
    logger = setup_logger(config)
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    
    # 设置上传文件夹
    app.config['UPLOAD_FOLDER'] = config['directories']['download']
    app.config['MAX_CONTENT_LENGTH'] = config['server']['max_content_length']
    app.config['CONFIG'] = config
    
    # 注册蓝图
    app.register_blueprint(api_bp)
    
    return app 