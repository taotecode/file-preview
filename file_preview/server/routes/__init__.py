"""
路由模块初始化文件
"""

from .api import api_bp
from .views import views_bp

# 导出所有蓝图
__all__ = ['api_bp', 'views_bp'] 