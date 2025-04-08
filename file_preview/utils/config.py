"""
配置文件加载工具
"""

import os
import yaml
from typing import Dict, Any

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径，如果为 None 则使用默认路径
        
    Returns:
        配置字典
    """
    if config_path is None:
        # 默认配置文件路径
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'config.yaml'
        )
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 确保必要的目录存在
    for dir_type in ['cache', 'download', 'convert', 'log']:
        dir_path = config['directories'][dir_type]
        os.makedirs(dir_path, exist_ok=True)
    
    return config 