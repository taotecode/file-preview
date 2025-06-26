"""
任务处理工具
"""

import os
import logging
import threading
import enum
from typing import Dict, Any, Callable, Optional, Tuple
from ..core.converter import FileConverter
from ..core.downloader import FileDownloader
from ..core.cache import CacheManager
from ..utils.file_utils import (get_file_info, is_supported_format, get_file_md5, 
                             get_url_md5, generate_file_response, process_file_conversion as process_file_conversion_util,
                             download_and_process_url as download_and_process_url_util,
                             process_excel_direct_preview as process_excel_direct_preview_util,
                             handle_file_by_id as handle_file_by_id_util,
                             process_url_file as process_url_file_util,
                             process_uploaded_file as process_uploaded_file_util)
from ..utils.mapping import FileMapping
from .utils_core import TaskUtils, FileUtils, MIME_TO_EXT, ResponseUtils
from urllib.parse import urlparse
import requests
import hashlib
import time

# 获取日志记录器
logger = logging.getLogger('file_preview')

# 存储转换任务状态
conversion_tasks = {}

class TaskStatus(enum.Enum):
    """任务状态枚举"""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'

def update_task_status(task_id: str, status: TaskStatus, progress: int = None, message: str = None, error: str = None):
    """
    更新任务状态
    
    Args:
        task_id: 任务ID
        status: 任务状态
        progress: 进度百分比（0-100）
        message: 状态信息
        error: 错误信息
    """
    logger.debug(f"更新任务状态: {task_id}, 状态: {status.value}, 进度: {progress}, 消息: {message}")
    
    if task_id not in conversion_tasks:
        conversion_tasks[task_id] = {}
    
    conversion_tasks[task_id]['status'] = status.value
    
    if progress is not None:
        conversion_tasks[task_id]['progress'] = progress
    
    if message:
        conversion_tasks[task_id]['message'] = message
        
    if error:
        conversion_tasks[task_id]['error'] = error

def get_url_content_type(url: str) -> Optional[str]:
    """
    获取URL的内容类型
    
    Args:
        url: URL
        
    Returns:
        内容类型或None
    """
    try:
        response = requests.head(url, timeout=10)
        response.raise_for_status()
        return response.headers.get('content-type')
    except Exception as e:
        logger.error(f"获取URL内容类型失败: {str(e)}")
        return None

# 使用新的工具类中的方法替代原有函数
create_task_id = TaskUtils.create_task_id
start_background_task = TaskUtils.start_background_task

def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    获取任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务状态
    """
    logger.info(f"获取任务状态: {task_id}, 当前任务列表: {list(conversion_tasks.keys())}")
    if task_id not in conversion_tasks:
        logger.warning(f"任务不存在: {task_id}")
        return None
    return conversion_tasks[task_id]

def process_file_conversion(task_id: str, file_path: str, config: Dict[str, Any], 
                          file_md5: Optional[str] = None, url_md5: Optional[str] = None,
                          original_name: Optional[str] = None) -> None:
    """
    处理文件转换（任务版本）
    
    Args:
        task_id: 任务ID
        file_path: 文件路径
        config: 配置信息
        file_md5: 文件MD5值
        url_md5: URL的MD5值
        original_name: 原始文件名
    """
    try:
        logger.info(f"开始处理文件转换，任务ID: {task_id}, 文件路径: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            # 获取项目根目录
            root_dir = FileUtils.get_project_root()
            
            # 检查几种可能的路径情况
            possible_paths = [
                file_path,  # 原始路径
                os.path.join(root_dir, file_path.lstrip("/")),  # 相对于根目录的路径
                os.path.join(root_dir, config['directories']['download'].lstrip("./"), os.path.basename(file_path))  # 下载目录
            ]
            
            # 尝试所有可能的路径
            file_found = False
            for possible_path in possible_paths:
                if os.path.exists(possible_path):
                    file_path = possible_path
                    file_found = True
                    logger.info(f"找到文件路径: {file_path}")
                    break
            
            if not file_found:
                logger.error(f"文件不存在: {file_path}")
                error_msg = f"[Errno 2] No such file or directory: '{file_path}'"
                conversion_tasks[task_id] = {
                    'status': 'failed',
                    'error': error_msg
                }
                return
        
        # 调用工具函数处理转换
        try:
            new_task_id, response = process_file_conversion_util(
                file_path=file_path,
                config=config,
                file_md5=file_md5,
                url_md5=url_md5,
                original_name=original_name
            )
            
            # 获取文件ID
            if file_md5 or url_md5:
                file_mapping = FileMapping(config)
                file_id = file_mapping.get_id_by_md5(file_md5 or url_md5) or response.get('file_id', '')
            else:
                file_id = response.get('file_id', '')
            
            # 更新任务状态
            if response["status"] == "success":
                # 生成下载URL和预览URL
                download_url = response.get('download_url', '')
                preview_url = response.get('preview_url', '')
                
                # 如果没有下载URL，则根据文件ID或文件名生成
                if not download_url and file_id:
                    download_url = f"/api/download?file_id={file_id}"
                
                # 如果没有预览URL，则根据文件ID或文件名生成
                if not preview_url and file_id:
                    preview_url = f"/preview?file_id={file_id}"
                
                conversion_tasks[task_id] = {
                    'status': 'completed',
                    'message': response.get('message', '文件转换成功'),
                    'file_id': file_id,
                    'download_url': download_url,
                    'preview_url': preview_url
                }
            else:
                conversion_tasks[task_id] = {
                    'status': 'failed',
                    'error': response.get('error', '转换失败')
                }
            
        except Exception as e:
            logger.error(f"转换过程中发生错误: {str(e)}", exc_info=True)
            conversion_tasks[task_id] = {
                'status': 'failed',
                'error': str(e)
            }
        
    except Exception as e:
        logger.error(f"处理文件转换任务失败: {str(e)}", exc_info=True)
        conversion_tasks[task_id] = {
            'status': 'failed',
            'error': str(e)
        }

def download_and_process_url(task_id: str, url: str, config: Dict[str, Any], url_md5: str = None) -> Dict[str, Any]:
    """
    下载并处理URL
    
    Args:
        task_id: 任务ID
        url: URL
        config: 配置信息
        url_md5: URL的MD5值
        
    Returns:
        处理结果
    """
    try:
        logger.info(f"开始下载并处理URL: {url}")
        
        # 初始化下载器和转换器
        downloader = FileDownloader(config)
        converter = FileConverter(config)
        file_mapping = FileMapping(config)
        
        # 更新任务状态
        conversion_tasks[task_id] = {
            'status': 'processing',
            'message': '正在下载文件...'
        }
        
        # 如果未提供URL的MD5，计算它
        if not url_md5:
            url_md5 = get_url_md5(url)
        
        # 检查是否已经处理过这个URL
        existing_file_id = file_mapping.get_id_by_url(url) or file_mapping.get_id_by_md5(url_md5)
        if existing_file_id:
            file_info = file_mapping.get_file_info(existing_file_id)
            if file_info and os.path.exists(file_info.get('path', '')):
                # 已存在处理结果，直接使用
                logger.info(f"URL已有处理结果: {url} -> {existing_file_id}")
                conversion_tasks[task_id] = {
                    'status': 'completed',
                    'message': '文件处理完成',
                    'file_id': existing_file_id,
                    'download_url': f"/api/download?file_id={existing_file_id}",
                    'preview_url': f"/preview?file_id={existing_file_id}",
                    'file_info': file_info
                }
                return conversion_tasks[task_id]
        
        # 下载文件
        temp_file_path = downloader.download(url)
        if not temp_file_path:
            logger.error(f"下载文件失败: {url}")
            conversion_tasks[task_id] = {
                'status': 'failed',
                'message': '下载文件失败',
                'error': f'无法下载文件: {url}'
            }
            return conversion_tasks[task_id]
            
        # 提取原始文件名
        original_filename = os.path.basename(temp_file_path)
        logger.info(f"文件下载完成: {temp_file_path}")
        
        # 获取原始文件信息
        original_file_info = get_file_info(temp_file_path)
        
        # 构建下载信息
        download_info = {
            'url': url,
            'download_time': time.time(),
            'original_filename': original_filename,
            'temp_path': temp_file_path,
            'url_md5': url_md5,
            'file_size': os.path.getsize(temp_file_path) if os.path.exists(temp_file_path) else 0,
            'file_extension': original_file_info.get('extension', '')
        }
        
        # 检查文件格式是否支持
        if not is_supported_format(temp_file_path, config):
            logger.error(f"不支持的文件格式: {temp_file_path}")
            conversion_tasks[task_id] = {
                'status': 'failed',
                'message': '不支持的文件格式',
                'error': f'不支持的文件格式: {os.path.basename(temp_file_path)}'
            }
            return conversion_tasks[task_id]
        
        # 使用FileProcessor处理文件
        try:
            from ..utils.file_processor import FileProcessor
            processor = FileProcessor(config)
            
            # 处理文件，包含详细信息
            response = processor.process_file(temp_file_path, url_md5, original_filename)
            
            # 添加URL映射信息
            if response.get('status') == 'success' and response.get('file_id'):
                # 获取文件ID
                file_id = response.get('file_id')
                
                # 确保URL映射已建立
                file_mapping._add_url_mapping(url, file_id)
                
                # 更新文件信息，添加下载信息
                file_info = file_mapping.get_file_info(file_id) or {}
                if file_info:
                    file_info['download_info'] = download_info
                    file_info['source_url'] = url
                    file_mapping.cache_manager.put_file_info(file_id, file_info)
                
                # 更新任务状态
                conversion_tasks[task_id] = {
                    'status': 'completed',
                    'message': '文件处理完成',
                    'file_id': file_id,
                    'download_url': response.get('download_url', f"/api/download?file_id={file_id}"),
                    'preview_url': response.get('preview_url', f"/preview?file_id={file_id}"),
                    'file_info': file_info,
                    'original_file_info': response.get('original_file_info'),
                    'converted_file_info': response.get('converted_file_info')
                }
            else:
                # 处理失败
                conversion_tasks[task_id] = {
                    'status': 'failed',
                    'message': '文件处理失败',
                    'error': response.get('error', '处理失败')
                }
                
        except Exception as e:
            logger.error(f"处理文件时发生错误: {str(e)}", exc_info=True)
            conversion_tasks[task_id] = {
                'status': 'failed',
                'message': '文件处理失败',
                'error': str(e)
            }
        finally:
            # 清理临时文件
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    logger.info(f"已删除临时文件: {temp_file_path}")
            except Exception as e:
                logger.error(f"删除临时文件失败: {str(e)}")
                
        return conversion_tasks[task_id]
            
    except Exception as e:
        logger.exception(f"处理URL失败: {str(e)}")
        conversion_tasks[task_id] = {
            'status': 'failed',
            'message': '处理URL失败',
            'error': str(e)
        }
        return conversion_tasks[task_id]

def process_task(task_type: str, task_id: str, config: Dict[str, Any], **kwargs) -> None:
    """
    处理任务
    
    Args:
        task_type: 任务类型
        task_id: 任务ID
        config: 配置信息
        **kwargs: 其他参数
    """
    # 初始化任务状态
    conversion_tasks[task_id] = {
        'status': 'processing',
        'task_type': task_type
    }
    
    try:
        logger.info(f"开始处理任务: {task_id}, 类型: {task_type}")
        
        # 根据任务类型处理
        if task_type == 'process_file' or task_type == 'file_path':
            # 处理文件路径
            process_file_conversion(
                task_id=task_id,
                file_path=kwargs.get('file_path'),
                config=config,
                file_md5=kwargs.get('file_md5'),
                url_md5=kwargs.get('url_md5'),
                original_name=kwargs.get('original_name')
            )
        elif task_type == 'process_url' or task_type == 'url':
            # 处理URL
            try:
                download_and_process_url(
                    task_id=task_id,
                    url=kwargs.get('url'),
                    config=config,
                    url_md5=kwargs.get('url_md5')
                )
            except NameError as e:
                # 如果update_task_status函数未定义，直接更新状态
                if "update_task_status" in str(e):
                    logger.error(f"函数未定义: {str(e)}，直接更新任务状态")
                    conversion_tasks[task_id] = {
                        'status': 'failed',
                        'error': 'URL处理失败: 内部函数未定义',
                        'message': '处理失败'
                    }
                else:
                    raise
        elif task_type == 'file_id':
            # 处理文件ID
            file_mapping = FileMapping(config)
            file_path, original_name = file_mapping.get_by_id(kwargs.get('file_id'))
            
            if not file_path:
                conversion_tasks[task_id]['status'] = 'failed'
                conversion_tasks[task_id]['error'] = f'找不到文件ID: {kwargs.get("file_id")}'
                return
                
            process_file_conversion(
                task_id=task_id,
                file_path=file_path,
                config=config,
                original_name=original_name
            )
        else:
            logger.error(f"未知任务类型: {task_type}")
            conversion_tasks[task_id]['status'] = 'failed'
            conversion_tasks[task_id]['error'] = f'未知任务类型: {task_type}'
            
    except Exception as e:
        logger.exception(f"任务处理失败: {task_id}, 错误: {str(e)}")
        conversion_tasks[task_id]['status'] = 'failed'
        conversion_tasks[task_id]['error'] = str(e)

def check_mapped_file(md5_hash: str, config: Dict[str, Any]) -> Optional[str]:
    """
    检查文件是否已经映射
    
    Args:
        md5_hash: MD5值
        config: 配置信息
    
    Returns:
        任务ID或None
    """
    file_mapping = FileMapping(config)
    mapped_pdf = file_mapping.get(md5_hash)
    
    if mapped_pdf:
        # 获取或创建文件ID
        file_id = file_mapping.get_id_by_md5(md5_hash) or ""
        
        # 生成任务ID
        task_id = create_task_id()
        conversion_tasks[task_id] = {
            'status': 'completed',
            'filename': os.path.basename(mapped_pdf),
            'file_id': file_id
        }
        return task_id
    
    return None

def create_conversion_task(file_id=None, file_path=None, url=None, uploaded_file=None, config=None, convert_to_pdf=True):
    """
    创建转换任务
    
    Args:
        file_id: 文件ID
        file_path: 文件路径
        url: 文件URL
        uploaded_file: 上传的文件对象
        config: 配置信息
        convert_to_pdf: 是否转换为PDF
        
    Returns:
        任务ID
    """
    # 首先检查是否已经有处理好的相同资源
    file_mapping = FileMapping(config)
    
    # 用于追踪可能的文件ID和MD5
    existing_file_id = None
    file_md5 = None
    url_md5 = None
    
    # 如果提供了URL，先检查是否已有缓存
    if url:
        url_md5 = get_url_md5(url)
        # 检查URL是否已经映射到文件ID
        cached_file_id = file_mapping.get_id_by_url(url)
        if cached_file_id:
            # 检查文件是否存在
            file_path, original_name = file_mapping.get_by_id(cached_file_id)
            if file_path and os.path.exists(file_path):
                logger.info(f"使用已缓存的URL: {url} -> {cached_file_id}")
                
                # 创建完成状态的任务
                task_id = create_task_id()
                # 构建响应URLs
                download_url = f"/api/download?file_id={cached_file_id}"
                preview_url = f"/preview?file_id={cached_file_id}"
                
                # 设置任务为完成状态
                conversion_tasks[task_id] = {
                    'status': 'completed',
                    'file_id': cached_file_id,
                    'download_url': download_url,
                    'preview_url': preview_url,
                    'message': '使用已缓存的文件',
                    'filename': original_name or os.path.basename(file_path)
                }
                return task_id
            else:
                # 记录URL MD5以便后续使用
                existing_file_id = cached_file_id
                
        # 检查是否有相同MD5的文件
        elif url_md5:
            cached_file_id = file_mapping.get_id_by_md5(url_md5)
            if cached_file_id:
                file_path, original_name = file_mapping.get_by_id(cached_file_id)
                if file_path and os.path.exists(file_path):
                    logger.info(f"使用具有相同MD5的缓存文件: {url_md5} -> {cached_file_id}")
                    
                    # 添加URL映射
                    file_mapping._add_url_mapping(url, cached_file_id)
                    
                    # 创建完成状态的任务
                    task_id = create_task_id()
                    # 构建响应URLs
                    download_url = f"/api/download?file_id={cached_file_id}"
                    preview_url = f"/preview?file_id={cached_file_id}"
                    
                    # 设置任务为完成状态
                    conversion_tasks[task_id] = {
                        'status': 'completed',
                        'file_id': cached_file_id,
                        'download_url': download_url,
                        'preview_url': preview_url,
                        'message': '使用已缓存的文件',
                        'filename': original_name or os.path.basename(file_path)
                    }
                    return task_id
                else:
                    # 记录URL MD5以便后续使用
                    existing_file_id = cached_file_id
    
    # 对于文件路径，检查文件MD5是否已经存在
    elif file_path and os.path.exists(file_path):
        file_md5 = get_file_md5(file_path)
        cached_file_id = file_mapping.get_id_by_md5(file_md5)
        if cached_file_id:
            cached_file_path, original_name = file_mapping.get_by_id(cached_file_id)
            if cached_file_path and os.path.exists(cached_file_path):
                logger.info(f"使用具有相同MD5的缓存文件: {file_md5} -> {cached_file_id}")
                
                # 创建完成状态的任务
                task_id = create_task_id()
                # 构建响应URLs
                download_url = f"/api/download?file_id={cached_file_id}"
                preview_url = f"/preview?file_id={cached_file_id}"
                
                # 设置任务为完成状态
                conversion_tasks[task_id] = {
                    'status': 'completed',
                    'file_id': cached_file_id,
                    'download_url': download_url,
                    'preview_url': preview_url,
                    'message': '使用已缓存的文件',
                    'filename': original_name or os.path.basename(cached_file_path)
                }
                return task_id
            else:
                # 记录文件MD5以便后续使用
                existing_file_id = cached_file_id
    
    # 如果提供了文件ID，检查该ID是否存在
    elif file_id:
        file_path, original_name = file_mapping.get_by_id(file_id)
        if file_path and os.path.exists(file_path):
            logger.info(f"使用已存在的文件ID: {file_id}")
            
            # 创建完成状态的任务
            task_id = create_task_id()
            # 构建响应URLs
            download_url = f"/api/download?file_id={file_id}"
            preview_url = f"/preview?file_id={file_id}"
            
            # 设置任务为完成状态
            conversion_tasks[task_id] = {
                'status': 'completed',
                'file_id': file_id,
                'download_url': download_url,
                'preview_url': preview_url,
                'message': '使用已存在的文件',
                'filename': original_name or os.path.basename(file_path)
            }
            return task_id
        else:
            # 记录文件ID以便后续使用
            existing_file_id = file_id
    
    # 如果没有找到缓存，创建新任务
    task_id = create_task_id()
    
    # 初始化任务状态，包含已知的元数据信息
    task_data = {
        'status': 'pending',
        'progress': 0,
        'message': '准备开始处理...'
    }
    
    # 添加已知的文件ID或MD5信息，这对API响应很有用
    if existing_file_id:
        task_data['file_id'] = existing_file_id
    if url_md5:
        task_data['url_md5'] = url_md5
    if file_md5:
        task_data['file_md5'] = file_md5
    if file_id:
        task_data['file_id'] = file_id
        
    conversion_tasks[task_id] = task_data
    
    # 根据提供的参数类型，决定处理方式
    if url:
        # URL处理
        start_background_task(download_and_process_url, task_id, url, config, url_md5=url_md5)
    elif uploaded_file:
        # 上传文件处理
        start_background_task(process_task, 'uploaded_file', task_id, config, uploaded_file=uploaded_file)
    elif file_path:
        # 文件路径处理
        start_background_task(process_file_conversion, task_id, file_path, config, file_md5=file_md5)
    elif file_id:
        # 文件ID处理
        start_background_task(process_task, 'file_id', task_id, config, file_id=file_id)
    else:
        # 参数错误
        conversion_tasks[task_id] = {
            'status': 'failed',
            'message': '参数错误',
            'error': '必须提供file_id、file_path、url或上传文件之一'
        }
    
    return task_id

def get_url_md5(url: str) -> str:
    """
    获取URL的MD5值
    
    Args:
        url: URL字符串
        
    Returns:
        MD5值
    """
    return hashlib.md5(url.encode()).hexdigest()