"""
文件工具
"""

import os
import hashlib
import logging
import time
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger('file_preview')

def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件信息字典
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    return {
        'name': os.path.basename(file_path),
        'size': os.path.getsize(file_path),
        'extension': os.path.splitext(file_path)[1].lower()
    }

def is_supported_format(file_path: str, config: Dict[str, Any]) -> bool:
    """
    检查文件格式是否支持
    
    Args:
        file_path: 文件路径
        config: 配置字典
        
    Returns:
        是否支持
    """
    try:
        file_info = get_file_info(file_path)
        return file_info['extension'] in config['conversion']['supported_formats']
    except Exception as e:
        logger.error(f"检查文件格式失败: {str(e)}", exc_info=True)
        return False

def get_file_md5(file_path: str) -> str:
    """
    计算文件的 MD5 值
    
    Args:
        file_path: 文件路径
        
    Returns:
        MD5 值
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_url_md5(url: str) -> str:
    """
    计算 URL 的 MD5 值
    
    Args:
        url: URL 字符串
        
    Returns:
        MD5 值
    """
    return hashlib.md5(url.encode()).hexdigest()

def generate_output_path(input_path: str, output_dir: str, keep_original_name: bool = True) -> str:
    """
    生成输出文件路径
    
    Args:
        input_path: 输入文件路径
        output_dir: 输出目录
        keep_original_name: 是否保留原始文件名
        
    Returns:
        输出文件路径
    """
    if keep_original_name:
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        return os.path.join(output_dir, f"{name}.pdf")
    else:
        return os.path.join(output_dir, f"{get_file_md5(input_path)}.pdf")

def cleanup_directory(directory: str, retention_days: int = 7) -> Tuple[int, int]:
    """
    清理目录中的文件
    
    Args:
        directory: 目录路径
        retention_days: 保留天数
        
    Returns:
        (删除的文件数, 删除的目录数)
    """
    if not os.path.exists(directory):
        return 0, 0
    
    now = time.time()
    file_count = 0
    dir_count = 0
    
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                if now - os.path.getmtime(file_path) > retention_days * 86400:
                    os.remove(file_path)
                    file_count += 1
            except Exception as e:
                logger.error(f"删除文件失败: {file_path}, 错误: {str(e)}")
        
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    dir_count += 1
            except Exception as e:
                logger.error(f"删除目录失败: {dir_path}, 错误: {str(e)}")
    
    return file_count, dir_count 