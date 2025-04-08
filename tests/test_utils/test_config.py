"""
配置加载工具测试
"""

import os
import pytest
import yaml
from file_preview.utils.config import load_config

def test_load_config(test_config: dict, temp_dir: str):
    """
    测试加载配置
    
    Args:
        test_config: 测试配置
        temp_dir: 临时目录路径
    """
    # 创建配置文件
    config_path = os.path.join(temp_dir, 'config.yaml')
    with open(config_path, 'w') as f:
        yaml.dump(test_config, f)
    
    # 加载配置
    config = load_config(config_path)
    
    # 验证配置
    assert config == test_config
    
    # 验证目录已创建
    for dir_type in ['cache', 'download', 'convert', 'log']:
        dir_path = config['directories'][dir_type]
        assert os.path.exists(dir_path)

def test_load_config_not_found():
    """
    测试加载不存在的配置文件
    """
    # 尝试加载不存在的配置文件
    with pytest.raises(FileNotFoundError):
        load_config('not_exist.yaml') 