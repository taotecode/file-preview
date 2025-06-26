"""
文件下载器
"""

import os
import logging
import requests
from typing import Optional
from urllib.parse import urlparse
from ..utils.file import get_file_info
import time

# 获取日志记录器
logger = logging.getLogger('file_preview')

class FileDownloader:
    """
    文件下载器，用于下载网络文件
    """
    
    def __init__(self, config: dict):
        """
        初始化下载器
        
        Args:
            config: 配置字典
        """
        self.download_dir = config['directories']['download']
        self.timeout = config['conversion']['timeout']
        
        # 确保下载目录存在
        os.makedirs(self.download_dir, exist_ok=True)
        
        logger.info(f"文件下载器初始化完成，下载目录: {self.download_dir}")
    
    def download(self, url: str) -> Optional[str]:
        """
        下载文件
        
        Args:
            url: 文件URL
            
        Returns:
            下载后的文件路径，如果下载失败则返回None
        """
        try:
            # 获取文件名
            filename = url.split('/')[-1]
            if '?' in filename:
                filename = filename.split('?')[0]
            
            # 处理文件名（确保文件名合法）
            if not filename:
                filename = f"downloaded_file_{int(time.time())}"
            
            # 获取项目根目录
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            
            # 获取下载目录的绝对路径
            download_dir_abs = os.path.join(root_dir, self.download_dir.lstrip("./"))
            
            # 确保下载目录存在
            os.makedirs(download_dir_abs, exist_ok=True)
            
            # 生成输出路径
            output_path = os.path.join(download_dir_abs, filename)
            
            logger.info(f"开始下载文件: {url} -> {output_path}")
            
            # 下载文件
            response = requests.get(url, stream=True, timeout=30)
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"下载失败，响应状态: {response.status_code}")
                return None
            
            # 写入文件
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 检查文件是否下载成功
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"文件下载成功: {output_path}, 大小: {os.path.getsize(output_path)} 字节")
                return output_path
            else:
                logger.error(f"文件下载失败: {output_path}")
                return None
            
        except Exception as e:
            logger.error(f"下载过程中发生错误: {str(e)}", exc_info=True)
            return None
    
    def cleanup(self, file_path: str) -> None:
        """
        清理下载的文件
        
        Args:
            file_path: 文件路径
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"已删除文件: {file_path}")
        except Exception as e:
            logger.error(f"删除文件时发生错误: {file_path}, 错误: {str(e)}", exc_info=True) 