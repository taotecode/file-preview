"""
配置文件加载工具
"""

import os
import yaml
from typing import Dict, Any

# 默认配置
DEFAULT_CONFIG = {
    'server': {
        'host': '0.0.0.0',
        'port': 5001
    },
    'directories': {
        'cache': './cache',
        'download': './download',
        'convert': './convert',
        'log': './logs',
        'upload': './upload'
    },
    'conversion': {
        'timeout': 60,
        'retry_times': 3,
        'libreoffice_path': 'libreoffice',
        'supported_formats': ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf']
    }
}

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径，如果为 None 则使用默认路径
        
    Returns:
        配置字典
    """
    config = DEFAULT_CONFIG.copy()
    
    if config_path is None:
        # 默认配置文件路径
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'config.yaml'
        )
    
    if isinstance(config_path, (str, bytes, os.PathLike)) and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                
            # 合并配置
            if loaded_config:
                for section, values in loaded_config.items():
                    if section in config and isinstance(values, dict):
                        config[section].update(values)
                    else:
                        config[section] = values
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}，使用默认配置")
    elif config_path is not None:
        print(f"配置文件不存在: {config_path}，使用默认配置")
    
    # 确保所有必要的配置部分都存在
    for section in ['server', 'directories', 'conversion']:
        if section not in config:
            config[section] = DEFAULT_CONFIG[section]
    
    # 确保必要的目录存在
    if 'directories' in config:
        for dir_type in ['cache', 'download', 'convert', 'log', 'upload']:
            if dir_type not in config['directories']:
                config['directories'][dir_type] = DEFAULT_CONFIG['directories'][dir_type]
            
            dir_path = config['directories'][dir_type]
            os.makedirs(dir_path, exist_ok=True)
    
    return config 