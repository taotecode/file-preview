"""
日志工具
"""

import os
import logging
from typing import Dict, Any

def setup_logger(config: Dict[str, Any]) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        config: 配置字典
        
    Returns:
        日志记录器
    """
    # 创建日志目录
    log_dir = config['directories']['log']
    os.makedirs(log_dir, exist_ok=True)
    
    # 获取日志记录器
    logger = logging.getLogger('file_preview')
    logger.setLevel(getattr(logging, config['logging']['level'].upper()))
    
    # 如果已经有处理器，不重复添加
    if logger.handlers:
        return logger
    
    # 创建文件处理器
    log_file = os.path.join(log_dir, 'file_preview.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(getattr(logging, config['logging']['level'].upper()))
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config['logging']['level'].upper()))
    
    # 创建格式化器
    formatter = logging.Formatter(config['logging']['format'])
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # 记录初始化信息
    logger.info("日志记录器初始化完成")
    
    return logger 