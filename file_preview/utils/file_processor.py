"""
文件处理工具类
提供统一的文件处理、转换和缓存功能
"""

import os
import logging
import time
from typing import Dict, Any, Optional, Tuple, List
from ..core.converter import FileConverter
from ..core.cache import CacheManager
from .file_utils import get_file_info, is_supported_format, get_file_md5, get_url_md5
from .mapping import FileMapping
from ..core.downloader import FileDownloader
from .utils_core import FileUtils

# 获取日志记录器
logger = logging.getLogger('file_preview')

class FileProcessor:
    """文件处理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化文件处理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.converter = FileConverter(config)
        self.cache_manager = CacheManager(config)
        self.file_mapping = FileMapping(config)
        self.downloader = FileDownloader(config)
    
    def process_file(self, file_path: str, file_md5: Optional[str] = None, 
                    original_name: Optional[str] = None) -> Dict[str, Any]:
        """
        处理文件，根据文件类型选择不同的处理方式
        
        Args:
            file_path: 文件路径
            file_md5: 文件MD5（可选）
            original_name: 原始文件名（可选）
            
        Returns:
            处理结果字典
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"输入文件不存在: {file_path}")
                return {
                    "status": "failed",
                    "message": "文件不存在",
                    "error": f"文件不存在: {file_path}"
                }
            
            # 获取原始文件信息
            original_file_info = get_file_info(file_path)
            logger.info(f"开始处理文件: {original_file_info}")
            
            # 检查文件格式
            if not is_supported_format(file_path, self.config):
                logger.error(f"不支持的文件格式: {original_file_info['extension']}")
                return {
                    "status": "failed",
                    "message": "不支持的文件类型",
                    "error": f"不支持的文件格式: {original_file_info['extension']}"
                }
            
            # 如果未提供 MD5，则计算文件 MD5
            if not file_md5:
                file_md5 = get_file_md5(file_path)
            
            # 获取文件扩展名（小写）
            extension = original_file_info['extension'].lower()
            
            # 获取原始文件名
            original_filename = original_name or os.path.basename(file_path)
            
            # 处理结果路径
            result_path = None
            
            # 记录转换过程
            conversion_method = ""
            conversion_time_start = time.time()
            
            # 根据文件类型选择不同的处理方式
            if extension in ['.doc', '.docx', '.ppt', '.pptx']:
                # 文档和演示文稿转换为PDF
                result_path = self._process_to_pdf(file_path, file_md5)
                conversion_method = "to_pdf"
            elif extension == '.xls':
                # XLS 转换为 XLSX
                result_path = self._process_xls_to_xlsx(file_path, file_md5)
                conversion_method = "xls_to_xlsx"
            elif extension == '.xlsx':
                # XLSX 直接缓存
                result_path = self._process_cache_only(file_path, file_md5)
                conversion_method = "cache_only"
            else:
                # 默认转换为PDF
                result_path = self._process_to_pdf(file_path, file_md5)
                conversion_method = "to_pdf"
            
            conversion_time_end = time.time()
            conversion_duration = conversion_time_end - conversion_time_start
            
            # 如果处理失败
            if not result_path:
                return {
                    "status": "failed",
                    "message": "文件处理失败",
                    "error": "处理过程中出错"
                }
            
            # 获取转换后的文件信息
            converted_file_info = get_file_info(result_path)
            
            # 构建详细的原始文件信息
            original_file_details = {
                'path': file_path,
                'filename': os.path.basename(file_path),
                'extension': original_file_info['extension'],
                'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'last_modified': os.path.getmtime(file_path) if os.path.exists(file_path) else 0,
                'md5': file_md5
            }
            
            # 获取转换后文件的MIME类型
            import mimetypes
            converted_mime_type = mimetypes.guess_type(result_path)[0] or 'application/octet-stream'
            
            # 构建详细的转换文件信息
            converted_file_details = {
                'path': result_path,
                'filename': os.path.basename(result_path),
                'extension': converted_file_info['extension'],
                'size': os.path.getsize(result_path) if os.path.exists(result_path) else 0,
                'conversion_method': conversion_method,
                'conversion_time': conversion_time_start,
                'conversion_duration': conversion_duration,
                'md5': get_file_md5(result_path) if os.path.exists(result_path) else "",
                'mime_type': converted_mime_type
            }
            
            # 添加文件映射，包含详细的原始和转换信息
            file_id = self.file_mapping.add(
                file_md5, 
                result_path, 
                original_filename,
                original_file_info=original_file_details,
                converted_info=converted_file_details
            )
            
            # 生成任务ID
            task_id = os.urandom(16).hex()
            
            # 生成响应
            response = {
                "status": "success",
                "message": "文件已处理",
                "task_id": task_id,
                "file_id": file_id,
                "filename": os.path.basename(result_path),
                "original_name": original_filename,
                "output_path": result_path,
                "file_type": converted_file_info['extension'].lstrip('.'),
                "original_file_info": original_file_details,
                "converted_file_info": converted_file_details
            }
            
            # 添加预览和下载URL
            if file_id:
                response["preview_url"] = f"/preview?file_id={file_id}"
                response["download_url"] = f"/api/download?file_id={file_id}"
            
            return response
            
        except Exception as e:
            logger.error(f"文件处理失败: {str(e)}", exc_info=True)
            return {
                "status": "failed",
                "message": "文件处理失败",
                "error": str(e)
            }
    
    def process_url(self, url: str) -> Dict[str, Any]:
        """
        处理URL指向的文件
        
        Args:
            url: 文件URL
            
        Returns:
            处理结果字典
        """
        try:
            # 计算URL的MD5
            url_md5 = FileUtils.get_url_md5(url)
            
            # 检查是否已经处理过该URL
            existing_file_id = self.file_mapping.get_id_by_url(url) or self.file_mapping.get_id_by_md5(url_md5)
            if existing_file_id:
                file_info = self.file_mapping.get_file_info(existing_file_id)
                if file_info and os.path.exists(file_info.get('path')):
                    # 文件已存在，直接返回信息
                    task_id = os.urandom(16).hex()
                    
                    # 构建响应
                    response = {
                        "status": "success",
                        "message": "URL文件已处理",
                        "task_id": task_id,
                        "file_id": existing_file_id,
                        "preview_url": f"/preview?file_id={existing_file_id}",
                        "download_url": f"/api/download?file_id={existing_file_id}"
                    }
                    
                    # 添加原始文件和转换文件信息（如果存在）
                    if 'original_file_info' in file_info:
                        response["original_file_info"] = file_info['original_file_info']
                    
                    if 'converted_info' in file_info:
                        response["converted_file_info"] = file_info['converted_info']
                        
                    return response
            
            # 下载文件
            file_path = self.downloader.download(url)
            if not file_path:
                return {
                    "status": "failed",
                    "message": "下载失败",
                    "error": "下载URL文件失败"
                }
            
            try:
                # 记录下载信息
                download_info = {
                    'url': url,
                    'download_time': time.time(),
                    'url_md5': url_md5
                }
                
                # 处理文件
                response = self.process_file(file_path, url_md5, os.path.basename(file_path))
                
                # 添加URL到文件映射
                if response["status"] == "success" and response.get("file_id"):
                    # 添加URL映射
                    self.file_mapping._add_url_mapping(url, response["file_id"])
                    
                    # 更新文件信息，添加下载信息
                    file_id = response["file_id"]
                    file_info = self.file_mapping.get_file_info(file_id) or {}
                    if file_info:
                        file_info['download_info'] = download_info
                        file_info['source_url'] = url
                        self.file_mapping.cache_manager.put_file_info(file_id, file_info)
                
                return response
            
            finally:
                # 删除下载的临时文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"删除临时文件: {file_path}")
        
        except Exception as e:
            logger.error(f"处理URL失败: {str(e)}", exc_info=True)
            return {
                "status": "failed",
                "message": "处理URL失败",
                "error": str(e)
            }
    
    def get_file_by_id(self, file_id: str) -> Dict[str, Any]:
        """
        通过文件ID获取文件
        
        Args:
            file_id: 文件ID
            
        Returns:
            文件信息字典
        """
        try:
            # 查询文件映射
            file_info = self.file_mapping.get_file_info(file_id)
            
            if not file_info:
                return {
                    "status": "failed",
                    "message": "文件不存在",
                    "error": f"找不到ID为 {file_id} 的文件"
                }
            
            file_path = file_info.get('path')
            
            if not file_path or not os.path.exists(file_path):
                return {
                    "status": "failed",
                    "message": "文件路径无效",
                    "error": f"文件路径 {file_path} 不存在"
                }
            
            # 获取文件信息
            path_info = get_file_info(file_path)
            
            return {
                "status": "success",
                "message": "获取文件成功",
                "file_id": file_id,
                "file_path": file_path,
                "original_name": file_info.get('original_name', os.path.basename(file_path)),
                "filename": path_info.get('filename'),
                "extension": path_info.get('extension'),
                "size": path_info.get('size'),
                "preview_url": f"/preview?file_id={file_id}",
                "download_url": f"/api/download?file_id={file_id}"
            }
        
        except Exception as e:
            logger.error(f"获取文件失败: {str(e)}", exc_info=True)
            return {
                "status": "failed",
                "message": "获取文件失败",
                "error": str(e)
            }
    
    def _process_to_pdf(self, file_path: str, file_md5: str) -> Optional[str]:
        """
        将文件转换为PDF并缓存
        
        Args:
            file_path: 文件路径
            file_md5: 文件MD5
            
        Returns:
            处理后的文件路径，失败则返回None
        """
        try:
            # 生成缓存键，使用特殊前缀
            cache_key = f"file_info:pdf_{file_md5}"
            
            # 尝试查找已转换的PDF文件
            cache_path = self.cache_manager.get(cache_key)
            if cache_path and os.path.exists(cache_path):
                logger.info(f"使用缓存的PDF文件: {cache_path}")
                return cache_path
            
            # 转换文件
            pdf_path = self.converter.convert(file_path)
            if not pdf_path:
                logger.error("PDF转换失败: 转换器返回空路径")
                return None
            
            # 保存到缓存
            self.cache_manager.backend.set(cache_key, pdf_path)
            
            return pdf_path
        except Exception as e:
            logger.error(f"PDF转换失败: {str(e)}", exc_info=True)
            return None
    
    def _process_xls_to_xlsx(self, file_path: str, file_md5: str) -> Optional[str]:
        """
        将XLS文件转换为XLSX并缓存
        
        Args:
            file_path: 文件路径
            file_md5: 文件MD5
            
        Returns:
            处理后的文件路径，失败则返回None
        """
        try:
            # 生成缓存键，使用特殊前缀
            cache_key = f"file_info:xlsx_{file_md5}"
            
            # 尝试查找已转换的XLSX文件
            cache_path = self.cache_manager.get(cache_key)
            if cache_path and os.path.exists(cache_path):
                logger.info(f"使用缓存的XLSX文件: {cache_path}")
                return cache_path
            
            # 转换文件
            xlsx_path = self.converter.convert_xls_to_xlsx(file_path)
            if not xlsx_path:
                logger.error("XLSX转换失败: 转换器返回空路径")
                return None
            
            # 保存到缓存
            self.cache_manager.backend.set(cache_key, xlsx_path)
            
            # 更新映射关系，确保文件ID指向转换后的XLSX文件
            try:
                # 获取现有文件ID
                existing_file_id = self.file_mapping.get_id_by_md5(file_md5)
                if existing_file_id:
                    # 更新文件路径
                    file_info = self.file_mapping.get_file_info(existing_file_id) or {}
                    if file_info:
                        # 保存原始路径以备参考
                        file_info['original_path'] = file_info.get('path', '')
                        # 更新为转换后的路径
                        file_info['path'] = xlsx_path
                        # 更新文件类型
                        file_info['extension'] = '.xlsx'
                        file_info['file_type'] = 'excel'
                        # 保存更新
                        self.file_mapping.cache_manager.put_file_info(existing_file_id, file_info)
                        logger.info(f"更新文件映射路径: {existing_file_id} -> {xlsx_path}")
            except Exception as e:
                logger.error(f"更新文件映射失败: {str(e)}", exc_info=True)
            
            return xlsx_path
        except Exception as e:
            logger.error(f"XLSX转换失败: {str(e)}", exc_info=True)
            return None
    
    def _process_cache_only(self, file_path: str, file_md5: str) -> Optional[str]:
        """
        仅缓存文件，不进行转换
        
        Args:
            file_path: 文件路径
            file_md5: 文件MD5
            
        Returns:
            处理后的文件路径，失败则返回None
        """
        try:
            # 生成缓存键，使用特殊前缀
            cache_key = f"file_info:original_{file_md5}"
            
            # 尝试查找已缓存的文件
            cache_path = self.cache_manager.get(cache_key)
            if cache_path and os.path.exists(cache_path):
                logger.info(f"使用已缓存的文件: {cache_path}")
                return cache_path
            
            # 获取文件信息
            file_info = get_file_info(file_path)
            
            # 获取项目根目录
            root_dir = FileUtils.get_project_root()
            
            # 获取转换目录的绝对路径
            convert_dir_abs = os.path.join(root_dir, self.config['directories']['convert'].lstrip("./"))
            
            # 确保转换目录存在
            os.makedirs(convert_dir_abs, exist_ok=True)
            
            # 生成输出路径
            output_filename = f"{os.path.splitext(file_info['filename'])[0]}{file_info['extension']}"
            output_path = os.path.join(convert_dir_abs, output_filename)
            
            # 如果文件不在转换目录中，复制它
            if file_path != output_path:
                import shutil
                shutil.copy2(file_path, output_path)
                logger.info(f"文件已复制到缓存目录: {output_path}")
            
            # 保存到缓存
            self.cache_manager.backend.set(cache_key, output_path)
            
            return output_path
        except Exception as e:
            logger.error(f"文件缓存失败: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def process_file_simple(file_path: str, config: Dict[str, Any]) -> str:
        """
        简化版的文件处理方法，用于与现有代码兼容
        
        Args:
            file_path: 文件路径
            config: 配置字典
            
        Returns:
            任务ID，如果失败则抛出异常
        """
        try:
            # 创建处理器实例
            processor = FileProcessor(config)
            
            # 处理文件
            response = processor.process_file(file_path)
            
            # 检查处理结果
            if response["status"] != "success":
                raise Exception(response.get("error", "处理失败"))
            
            # 返回任务ID
            return response["task_id"]
            
        except Exception as e:
            logger.error(f"简化文件处理失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def process_url_simple(url: str, config: Dict[str, Any]) -> str:
        """
        简化版的URL处理方法，用于与现有代码兼容
        
        Args:
            url: 文件URL
            config: 配置字典
            
        Returns:
            任务ID，如果失败则抛出异常
        """
        try:
            # 创建处理器实例
            processor = FileProcessor(config)
            
            # 处理URL
            response = processor.process_url(url)
            
            # 检查处理结果
            if response["status"] != "success":
                raise Exception(response.get("error", "处理失败"))
            
            # 返回任务ID
            return response["task_id"]
            
        except Exception as e:
            logger.error(f"简化URL处理失败: {str(e)}", exc_info=True)
            raise 