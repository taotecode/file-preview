"""
服务器模块
"""

from .app import create_app
from .routes import api_bp

__all__ = ['create_app', 'api_bp'] 