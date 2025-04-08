"""
文件下载器
"""

import os
import logging
import requests
from typing import Optional
from urllib.parse import urlparse
from ..utils.file import get_file_info

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
            下载的文件路径，如果下载失败则返回None
        """
        try:
            # 解析URL获取文件名
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename:
                filename = 'downloaded_file'
            
            # 生成输出路径
            output_path = os.path.join(self.download_dir, filename)
            
            logger.info(f"开始下载文件: {url} -> {output_path}")
            
            # 下载文件
            response = requests.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()  # 检查HTTP错误
            
            # 保存文件
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"文件下载成功: {output_path}")
            return output_path
            
        except requests.exceptions.Timeout:
            logger.error(f"下载超时: {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"连接错误: {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP错误: {url}, 状态码: {e.response.status_code}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"下载请求错误: {url}, 错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"下载文件时发生未知错误: {url}, 错误: {str(e)}", exc_info=True)
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