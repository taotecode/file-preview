"""
文件转换器
"""

import os
import logging
import subprocess
from typing import Optional
from ..utils.file import get_file_info, is_supported_format

# 获取日志记录器
logger = logging.getLogger('file_preview')

class FileConverter:
    """
    文件转换器
    """
    
    def __init__(self, config: dict):
        """
        初始化转换器
        
        Args:
            config: 配置字典
        """
        self.convert_dir = config['directories']['convert']
        self.timeout = config['conversion']['timeout']
        self.retry_times = config['conversion']['retry_times']
        self.libreoffice_path = config['conversion']['libreoffice_path']
        
        # 确保转换目录存在
        os.makedirs(self.convert_dir, exist_ok=True)
        
        logger.info(f"文件转换器初始化完成，转换目录: {self.convert_dir}")
    
    def convert(self, input_path: str) -> Optional[str]:
        """
        转换文件为PDF
        
        Args:
            input_path: 输入文件路径
            
        Returns:
            转换后的PDF文件路径，如果转换失败则返回None
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(input_path):
                logger.error(f"输入文件不存在: {input_path}")
                return None
            
            # 获取文件信息
            file_info = get_file_info(input_path)
            logger.info(f"开始转换文件: {file_info}")
            
            # 检查文件格式
            if not is_supported_format(input_path, {'conversion': {'supported_formats': ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']}}):
                logger.error(f"不支持的文件格式: {file_info['extension']}")
                return None
            
            # 生成输出路径
            output_path = os.path.join(
                self.convert_dir,
                f"{os.path.splitext(file_info['name'])[0]}.pdf"
            )
            
            # 如果输出文件已存在，直接返回
            if os.path.exists(output_path):
                logger.info(f"输出文件已存在: {output_path}")
                return output_path
            
            # 构建转换命令
            cmd = [
                self.libreoffice_path,
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', self.convert_dir,
                input_path
            ]
            
            logger.info(f"执行转换命令: {' '.join(cmd)}")
            
            # 尝试转换
            for attempt in range(self.retry_times):
                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    
                    # 等待进程完成
                    stdout, stderr = process.communicate(timeout=self.timeout)
                    
                    # 检查返回码
                    if process.returncode == 0:
                        logger.info(f"文件转换成功: {output_path}")
                        return output_path
                    else:
                        logger.warning(f"转换失败 (尝试 {attempt + 1}/{self.retry_times}): {stderr.decode()}")
                        
                except subprocess.TimeoutExpired:
                    logger.warning(f"转换超时 (尝试 {attempt + 1}/{self.retry_times})")
                    process.kill()
                    process.communicate()
                except Exception as e:
                    logger.error(f"转换过程中发生错误 (尝试 {attempt + 1}/{self.retry_times}): {str(e)}", exc_info=True)
            
            logger.error(f"转换失败，已达到最大重试次数: {self.retry_times}")
            return None
            
        except Exception as e:
            logger.error(f"转换文件时发生未知错误: {str(e)}", exc_info=True)
            return None 