"""
日志工具测试
"""

import os
import logging
from file_preview.utils.logger import setup_logger

def test_setup_logger(test_config: dict):
    """
    测试设置日志
    
    Args:
        test_config: 测试配置
    """
    # 设置日志
    logger = setup_logger(test_config)
    
    # 验证日志器
    assert isinstance(logger, logging.Logger)
    assert logger.name == 'file_preview'
    assert logger.level == logging.DEBUG
    
    # 验证日志文件
    log_file = os.path.join(test_config['directories']['log'], 'file_preview.log')
    assert os.path.exists(log_file)
    
    # 验证处理器
    assert len(logger.handlers) == 2
    assert isinstance(logger.handlers[0], logging.FileHandler)
    assert isinstance(logger.handlers[1], logging.StreamHandler)
    
    # 验证格式化器
    for handler in logger.handlers:
        assert isinstance(handler.formatter, logging.Formatter)
        assert handler.formatter._fmt == test_config['logging']['format']
    
    # 测试日志记录
    test_message = '测试日志消息'
    logger.info(test_message)
    
    # 验证日志内容
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert test_message in log_content 