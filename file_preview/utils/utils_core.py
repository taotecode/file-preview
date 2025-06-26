"""
核心工具类
提供整合后的通用功能
"""

import os
import logging
import hashlib
import time
import uuid
import base64
import mimetypes
import threading
from typing import Dict, Any, Optional, Tuple, List, Callable, Union

# 获取日志记录器
logger = logging.getLogger('file_preview')

# MIME类型到扩展名的映射
MIME_TO_EXT = {
    'application/pdf': '.pdf',
    'application/msword': '.doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'application/vnd.ms-excel': '.xls',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
    'application/vnd.ms-powerpoint': '.ppt',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
}

# 扩展名到文件类型的映射
EXT_TO_TYPE = {
    '.pdf': 'pdf',
    '.doc': 'word',
    '.docx': 'word',
    '.xls': 'excel',
    '.xlsx': 'excel',
    '.ppt': 'powerpoint',
    '.pptx': 'powerpoint',
    '.jpg': 'image',
    '.jpeg': 'image',
    '.png': 'image',
    '.gif': 'image',
    '.bmp': 'image',
    '.txt': 'text',
    '.csv': 'text',
    '.json': 'text',
    '.xml': 'text',
    '.html': 'text',
    '.htm': 'text',
}

# 默认支持的文件格式
DEFAULT_SUPPORTED_FORMATS = [
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
    '.ppt', '.pptx', '.txt', '.rtf', '.odt',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp'
]

class FileUtils:
    """文件处理通用工具类"""
    
    @staticmethod
    def get_file_md5(file_path: str) -> str:
        """
        计算文件的MD5值
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件的MD5值，失败时返回空字符串
        """
        if not os.path.exists(file_path):
            logger.error(f"计算MD5失败: 文件不存在 {file_path}")
            return ""
            
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"计算文件MD5失败: {str(e)}")
            return ""
    
    @staticmethod
    def get_url_md5(url: str) -> str:
        """
        计算URL的MD5值
        
        Args:
            url: URL字符串
            
        Returns:
            URL的MD5值
        """
        return hashlib.md5(url.encode('utf-8')).hexdigest()
    
    @staticmethod
    def get_string_md5(text: str) -> str:
        """
        计算字符串的MD5值
        
        Args:
            text: 字符串
            
        Returns:
            字符串的MD5值
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含文件信息的字典
        """
        if not os.path.exists(file_path):
            # 检查是否为相对路径
            file_name = os.path.basename(file_path)
            if file_name != file_path:
                # 只返回基本信息
                extension = os.path.splitext(file_path)[1].lower()
                return {
                    "exists": False,
                    "filename": file_name,
                    "size": 0,
                    "extension": extension,
                    "mime_type": mimetypes.guess_type(file_path)[0] or "application/octet-stream",
                    "file_type": EXT_TO_TYPE.get(extension, "other")
                }
                
            return {
                "exists": False,
                "filename": file_path,
                "size": 0,
                "extension": os.path.splitext(file_path)[1].lower(),
                "mime_type": mimetypes.guess_type(file_path)[0] or "application/octet-stream"
            }
        
        file_stats = os.stat(file_path)
        file_name = os.path.basename(file_path)
        extension = os.path.splitext(file_path)[1].lower()
        
        # 获取MIME类型
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            # 使用提前定义的映射
            mime_type = next((mime for mime, ext in MIME_TO_EXT.items() if ext == extension), 'application/octet-stream')
        
        # 文件类型
        file_type = EXT_TO_TYPE.get(extension, "other")
        
        return {
            "exists": True,
            "filename": file_name,
            "path": file_path,
            "size": file_stats.st_size,
            "extension": extension,
            "mime_type": mime_type,
            "file_type": file_type,
            "modified_time": file_stats.st_mtime
        }
    
    @staticmethod
    def is_supported_format(file_path: str, config: Dict[str, Any]) -> bool:
        """
        检查文件格式是否支持
        
        Args:
            file_path: 文件路径
            config: 配置信息
            
        Returns:
            是否支持
        """
        # 获取支持的文件扩展名列表
        supported_extensions = config.get('supported_extensions', [])
        
        # 如果未配置支持的扩展名，尝试从conversion中获取
        if not supported_extensions:
            supported_extensions = config.get('conversion', {}).get('supported_formats', [])
            
        # 如果仍无配置，使用默认列表
        if not supported_extensions:
            supported_extensions = DEFAULT_SUPPORTED_FORMATS
        
        # 获取文件扩展名
        extension = os.path.splitext(file_path)[1].lower()
        
        # 检查是否在支持列表中
        return extension in supported_extensions
    
    @staticmethod
    def generate_unique_id(length: int = 8) -> str:
        """
        生成唯一ID
        
        Args:
            length: ID长度
            
        Returns:
            唯一ID
        """
        # 生成UUID并取前部分，转为Base64编码
        raw_id = str(uuid.uuid4().hex)[:length*2]
        # 使用Base64编码但替换特殊字符，使其URL友好
        unique_id = base64.b64encode(raw_id.encode()).decode()
        unique_id = unique_id.replace('+', '-').replace('/', '_').replace('=', '')[:length]
        
        return unique_id
    
    @staticmethod
    def ensure_dir(directory: str) -> bool:
        """
        确保目录存在
        
        Args:
            directory: 目录路径
            
        Returns:
            是否成功创建或已存在
        """
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"创建目录失败: {directory}, 错误: {str(e)}")
            return False
    
    @staticmethod
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
    
    @staticmethod
    def get_project_root() -> str:
        """
        获取项目根目录
        
        Returns:
            项目根目录路径
        """
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    
    @staticmethod
    def normalize_path(path: str, base_dir: Optional[str] = None) -> str:
        """
        规范化路径
        
        Args:
            path: 原路径
            base_dir: 基准目录，默认为项目根目录
            
        Returns:
            规范化后的路径
        """
        if os.path.isabs(path):
            return path
            
        if base_dir is None:
            base_dir = FileUtils.get_project_root()
            
        return os.path.join(base_dir, path.lstrip("./"))


class TaskUtils:
    """任务处理通用工具类"""
    
    @staticmethod
    def create_task_id() -> str:
        """
        创建任务ID
        
        Returns:
            任务ID
        """
        return os.urandom(16).hex()
    
    @staticmethod
    def start_background_task(task_function: Callable, *args, **kwargs) -> None:
        """
        启动后台任务
        
        Args:
            task_function: 任务函数
            *args: 位置参数
            **kwargs: 关键字参数
        """
        thread = threading.Thread(target=task_function, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()


class ResponseUtils:
    """响应工具类"""
    
    @staticmethod
    def generate_success_response(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
        """
        生成成功响应
        
        Args:
            data: 数据
            message: 消息
            
        Returns:
            响应字典
        """
        response = {
            "status": "success",
            "message": message
        }
        
        if data is not None:
            if isinstance(data, dict):
                response.update(data)
            else:
                response["data"] = data
                
        return response
    
    @staticmethod
    def generate_error_response(error: str = "操作失败", details: Any = None) -> Dict[str, Any]:
        """
        生成错误响应
        
        Args:
            error: 错误信息
            details: 错误详情
            
        Returns:
            响应字典
        """
        response = {
            "status": "failed",
            "message": "操作失败",
            "error": error
        }
        
        if details is not None:
            response["details"] = details
            
        return response 