"""
文件处理工具
"""

import os
import logging
import hashlib
import mimetypes
from typing import Dict, Any, Optional, Tuple
from ..core.converter import FileConverter
from ..core.downloader import FileDownloader
from ..core.cache import CacheManager
from ..utils.mapping import FileMapping
from .utils_core import FileUtils, MIME_TO_EXT, DEFAULT_SUPPORTED_FORMATS

# 获取日志记录器
logger = logging.getLogger('file_preview')

# 为了兼容性，保留原来的函数名，但使用新的实现
get_file_md5 = FileUtils.get_file_md5
get_url_md5 = FileUtils.get_url_md5
get_file_info = FileUtils.get_file_info
is_supported_format = FileUtils.is_supported_format

def is_supported_file(file_path: str) -> bool:
    """
    检查文件是否支持（兼容函数）
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否支持
    """
    # 使用默认的常量配置
    config = {'supported_extensions': DEFAULT_SUPPORTED_FORMATS}
    return is_supported_format(file_path, config)

def save_uploaded_file(file, filename: str) -> str:
    """
    保存上传的文件
    
    Args:
        file: 上传的文件对象
        filename: 文件名
        
    Returns:
        保存后的文件路径
    """
    # 获取项目根目录
    root_dir = FileUtils.get_project_root()
    
    # 创建上传目录
    upload_dir = os.path.join(root_dir, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)
    
    return file_path

def generate_file_response(file_path: str, file_id: str, original_name: str = None, 
                          action: str = 'preview', convert_to_pdf: bool = False) -> Dict[str, Any]:
    """
    生成文件响应
    
    Args:
        file_path: 文件路径
        file_id: 文件ID
        original_name: 原始文件名
        action: 操作类型（preview, download, convert）
        convert_to_pdf: 是否转换为PDF
        
    Returns:
        响应字典
    """
    # 获取文件信息
    file_info = get_file_info(file_path)
    file_type = file_info['extension'].lower().strip('.')
    
    # 生成基础响应
    response = {
        "status": "success",
        "filename": original_name or os.path.basename(file_path),
        "file_id": file_id
    }
    
    # 生成下载URL
    basename = os.path.basename(file_path)
    if file_id:
        response["download_url"] = f"/api/download?file_id={file_id}"
    else:
        response["download_url"] = f"/api/download?file_path={basename}"
    
    # 生成预览URL
    if action == 'preview':
        if file_type in ['xls', 'xlsx'] and not convert_to_pdf:
            response["message"] = "Excel文件已准备好直接预览"
            if file_id:
                response["preview_url"] = f"/preview?file_id={file_id}&convert_to_pdf=false"
            else:
                response["preview_url"] = f"/preview?file={basename}&convert_to_pdf=false"
        elif file_type == "pdf" or convert_to_pdf:
            response["message"] = "文件已准备好预览"
            if file_id:
                response["preview_url"] = f"/preview?file_id={file_id}"
            else:
                response["preview_url"] = f"/preview?file={basename}"
        else:
            response["message"] = "文件已处理"
    elif action == 'convert':
        response["message"] = "文件已转换"
        if file_type == "pdf" or convert_to_pdf:
            if file_id:
                response["preview_url"] = f"/preview?file_id={file_id}"
            else:
                response["preview_url"] = f"/preview?file={basename}"
    
    return response

def process_file_conversion(file_path: str, config: Dict[str, Any], 
                          file_md5: Optional[str] = None, url_md5: Optional[str] = None,
                          original_name: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """
    处理文件转换
    
    Args:
        file_path: 文件路径
        config: 配置信息
        file_md5: 文件MD5值
        url_md5: URL的MD5值
        original_name: 原始文件名
        
    Returns:
        (任务ID, 响应字典)
    """
    # 这个函数在未来可以迁移到 FileProcessor 类中的 process_file 方法
    # 保留原始实现以确保兼容性
    try:
        # 确认文件存在
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
                return None, {
                    "status": "failed",
                    "message": "文件不存在",
                    "error": f"[Errno 2] No such file or directory: '{file_path}'"
                }
        
        # 检查文件类型
        if not is_supported_format(file_path, config):
            return None, {
                "status": "failed",
                "message": "不支持的文件类型",
                "error": "不支持的文件类型"
            }
        
        # 转换文件
        converter = FileConverter(config)
        cache_manager = CacheManager(config)
        
        # 检查缓存
        if cache_manager.exists(file_path):
            pdf_path = cache_manager.get(file_path)
        else:
            pdf_path = converter.convert(file_path)
            if not pdf_path:
                return None, {
                    "status": "failed",
                    "message": "转换失败",
                    "error": "转换失败"
                }
            
            # 添加到缓存
            cache_manager.put(file_path, pdf_path)
        
        # 添加文件映射
        file_mapping = FileMapping(config)
        md5_key = file_md5 or url_md5
        file_id = ""
        if md5_key:
            file_id = file_mapping.add(md5_key, pdf_path, original_name or os.path.basename(file_path))
        
        # 生成任务ID
        task_id = os.urandom(16).hex()
        
        return task_id, {
            "status": "success",
            "message": "文件已转换",
            "task_id": task_id,
            "filename": os.path.basename(pdf_path),
            "file_id": file_id
        }
        
    except Exception as e:
        logger.error(f"文件处理失败: {str(e)}", exc_info=True)
        return None, {
            "status": "failed",
            "message": "文件处理失败",
            "error": str(e)
        }

def download_and_process_url(url: str, config: Dict[str, Any], url_md5: str) -> Tuple[str, Dict[str, Any]]:
    """
    下载并处理URL指向的文件
    
    Args:
        url: 文件URL
        config: 配置信息
        url_md5: URL的MD5值
        
    Returns:
        (任务ID, 响应字典)
    """
    try:
        # 下载文件
        downloader = FileDownloader(config)
        file_path = downloader.download(url)
        if not file_path:
            return None, {
                "status": "failed",
                "message": "下载失败",
                "error": "下载失败"
            }
        
        try:
            # 处理文件转换
            task_id, response = process_file_conversion(
                file_path=file_path,
                config=config,
                url_md5=url_md5,
                original_name=os.path.basename(file_path)
            )
            
            # 确保响应中包含文件ID
            if response["status"] == "success" and not response.get("file_id") and url_md5:
                file_mapping = FileMapping(config)
                file_id = file_mapping.get_id_by_md5(url_md5)
                if file_id:
                    response["file_id"] = file_id
                    
            return task_id, response
        finally:
            # 删除下载的临时文件
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        logger.error(f"URL处理失败: {str(e)}", exc_info=True)
        return None, {
            "status": "failed",
            "message": "URL处理失败",
            "error": str(e)
        }

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
        # 生成任务ID
        task_id = os.urandom(16).hex()
        return task_id
    
    return None

def process_excel_direct_preview(file_path: str, filename: str, config: Dict[str, Any], file_md5: str = None) -> Dict[str, Any]:
    """
    处理Excel文件直接预览
    
    Args:
        file_path: 文件路径
        filename: 文件名
        config: 配置信息
        file_md5: 文件MD5值
        
    Returns:
        包含文件ID和响应的字典
    """
    # 如果没有提供MD5，计算文件MD5
    if not file_md5:
        file_md5 = get_file_md5(file_path)
    
    # 确保文件在下载目录中（如果需要）
    download_dir = config['directories']['download']
    target_path = os.path.join(download_dir, filename)
    
    if file_path != target_path and not os.path.exists(target_path):
        # 若文件不在下载目录，复制或移动到下载目录
        os.makedirs(download_dir, exist_ok=True)
        if os.path.dirname(file_path) != download_dir:
            import shutil
            shutil.copy2(file_path, target_path)
            file_path = target_path
    
    # 添加文件映射并获取文件ID
    file_mapping = FileMapping(config)
    file_id = file_mapping.add(file_md5, file_path, filename)
    
    # 生成响应
    response = generate_file_response(
        file_path=file_path,
        file_id=file_id,
        original_name=filename,
        action='preview',
        convert_to_pdf=False
    )
    
    return {"file_id": file_id, "response": response}

def handle_file_by_id(file_id: str, config: Dict[str, Any], action: str = 'preview', convert_to_pdf: bool = False) -> Optional[Dict[str, Any]]:
    """
    通过文件ID处理文件
    
    Args:
        file_id: 文件ID
        config: 配置信息
        action: 操作类型（preview, download, convert）
        convert_to_pdf: 是否转换为PDF
        
    Returns:
        响应字典或None（如果文件不存在）
    """
    # 获取映射
    file_mapping = FileMapping(config)
    file_path, original_name = file_mapping.get_by_id(file_id)
    
    if not file_path or not os.path.exists(file_path):
        return None
    
    # 生成响应
    return generate_file_response(
        file_path=file_path,
        file_id=file_id,
        original_name=original_name,
        action=action,
        convert_to_pdf=convert_to_pdf
    )

def process_url_file(url: str, config: Dict[str, Any], action: str = 'preview', convert_to_pdf: bool = False) -> Dict[str, Any]:
    """
    处理URL文件
    
    Args:
        url: 文件URL
        config: 配置信息
        action: 操作类型（preview, download, convert）
        convert_to_pdf: 是否转换为PDF
        
    Returns:
        响应字典
    """
    # 计算URL MD5
    url_md5 = get_url_md5(url)
    
    # 检查文件映射
    file_mapping = FileMapping(config)
    file_id = file_mapping.get_id_by_md5(url_md5)
    
    # 如果文件已经存在
    if file_id:
        file_path, original_name = file_mapping.get_by_id(file_id)
        if file_path and os.path.exists(file_path):
            return generate_file_response(
                file_path=file_path,
                file_id=file_id,
                original_name=original_name,
                action=action,
                convert_to_pdf=convert_to_pdf
            )
    
    # 如果是下载操作
    if action == 'download':
        # 下载文件
        downloader = FileDownloader(config)
        file_path = downloader.download(url)
        if not file_path:
            return {
                "status": "failed",
                "message": "下载文件失败",
                "error": "无法从URL下载文件"
            }
        
        try:
            # 获取文件名和类型
            filename = os.path.basename(file_path)
            
            # 移动到下载目录
            target_path = os.path.join(config['directories']['download'], filename)
            if file_path != target_path and not os.path.exists(target_path):
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                os.rename(file_path, target_path)
                file_path = target_path
            
            # 添加文件映射
            file_id = file_mapping.add(url_md5, file_path, filename)
            
            # 生成响应
            return generate_file_response(
                file_path=file_path,
                file_id=file_id,
                original_name=filename,
                action='download',
                convert_to_pdf=False
            )
        finally:
            # 确保文件被处理
            if os.path.exists(file_path) and file_path != target_path:
                os.remove(file_path)
    
    # 对于Excel文件的直接预览或其他预览/转换操作，使用异步处理
    # 生成任务ID
    task_id = os.urandom(16).hex()
    
    # 返回处理中的状态
    return {
        "status": "processing",
        "task_id": task_id,
        "message": "文件正在处理中",
        "check_url": f"/api/convert/status/{task_id}"
    }

def process_uploaded_file(file_path: str, filename: str, config: Dict[str, Any], 
                        action: str = 'preview', convert_to_pdf: bool = False) -> Dict[str, Any]:
    """
    处理上传的文件
    
    Args:
        file_path: 文件路径
        filename: 文件名
        config: 配置信息
        action: 操作类型（preview, download, convert）
        convert_to_pdf: 是否转换为PDF
        
    Returns:
        响应字典
    """
    # 确认文件存在
    if not os.path.exists(file_path):
        # 获取项目根目录
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        
        # 检查几种可能的路径情况
        possible_paths = [
            file_path,  # 原始路径
            os.path.join(root_dir, file_path.lstrip("/")),  # 相对于根目录的路径
            os.path.join(root_dir, config['directories']['download'].lstrip("./"), filename)  # 下载目录
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
            return {
                "status": "failed",
                "message": "文件不存在",
                "error": f"[Errno 2] No such file or directory: '{file_path}'"
            }
            
    # 计算文件MD5
    file_md5 = get_file_md5(file_path)
    
    # 检查文件映射
    file_mapping = FileMapping(config)
    existing_file_id = file_mapping.get_id_by_md5(file_md5)
    
    # 如果文件已经存在
    if existing_file_id:
        mapped_path, original_name = file_mapping.get_by_id(existing_file_id)
        if mapped_path and os.path.exists(mapped_path):
            return generate_file_response(
                file_path=mapped_path,
                file_id=existing_file_id,
                original_name=original_name or filename,
                action=action,
                convert_to_pdf=convert_to_pdf
            )
    
    # 检查文件类型
    file_info = get_file_info(file_path)
    is_excel = file_info['extension'].lower() in ['.xls', '.xlsx']
    
    # 如果是Excel文件且不需要转PDF，并且操作为预览
    if is_excel and not convert_to_pdf and action == 'preview':
        # 处理Excel直接预览
        result = process_excel_direct_preview(file_path, filename, config, file_md5)
        return result['response']
    
    # 如果操作为下载原始文件
    if action == 'download':
        # 确保文件在下载目录中
        download_dir = config['directories']['download']
        target_path = os.path.join(download_dir, filename)
        
        if file_path != target_path and not os.path.exists(target_path):
            os.makedirs(download_dir, exist_ok=True)
            # 复制文件到下载目录
            import shutil
            shutil.copy2(file_path, target_path)
            file_path = target_path
        
        # 添加文件映射
        file_id = file_mapping.add(file_md5, file_path, filename)
        
        # 生成响应
        return generate_file_response(
            file_path=file_path,
            file_id=file_id,
            original_name=filename,
            action='download',
            convert_to_pdf=False
        )
    
    # 对于需要转换的操作，使用异步处理
    # 生成任务ID
    task_id = os.urandom(16).hex()
    
    # 返回处理中的状态
    return {
        "status": "processing",
        "task_id": task_id,
        "message": "文件正在处理中",
        "check_url": f"/api/convert/status/{task_id}"
    } 