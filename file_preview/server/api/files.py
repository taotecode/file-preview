"""
文件下载和预览API
"""

from flask import request, jsonify, send_file, abort, current_app
from file_preview.utils.tasks import get_file_info
from file_preview.core.cache import CacheManager
import os
import mimetypes
import logging

# 获取日志记录器
logger = logging.getLogger('file_preview')

def download_file(file_path, is_file_id=False):
    """
    下载文件
    
    Args:
        file_path: 文件路径或文件ID
        is_file_id: 是否是文件ID
        
    Returns:
        文件响应
    """
    try:
        # 获取配置
        config = current_app.config['CONFIG']
        original_name = None
        file_info = None
        converted_info = None
        
        # 根据是否是文件ID处理
        if is_file_id:
            # 获取文件映射
            from file_preview.utils.mapping import FileMapping
            file_mapping = FileMapping(config)
            
            # 获取文件详细信息
            file_info = file_mapping.get_file_info(file_path)
            if file_info:
                # 尝试获取转换信息
                converted_info = file_info.get('converted_info')
                
                # 如果有转换信息，直接使用转换后的文件路径
                if converted_info and 'path' in converted_info and os.path.exists(converted_info['path']):
                    logger.info(f"使用转换文件信息: {converted_info}")
                    file_path = converted_info['path']
                    original_name = file_info.get('original_name')
                elif 'path' in file_info and os.path.exists(file_info['path']):
                    # 使用文件信息中的路径
                    file_path = file_info['path']
                    original_name = file_info.get('original_name')
                    logger.info(f"使用文件信息中的路径: {file_path}")
                else:
                    # 如果文件信息中的路径不存在，尝试使用get_by_id
                    mapped_path, original_name = file_mapping.get_by_id(file_path)
                    if not mapped_path:
                        return jsonify({
                            "status": "failed",
                            "message": "找不到文件",
                            "error": f"文件ID不存在: {file_path}"
                        }), 404
                    file_path = mapped_path
            else:
                # 如果没有找到文件信息，使用get_by_id
                mapped_path, original_name = file_mapping.get_by_id(file_path)
                if not mapped_path:
                    return jsonify({
                        "status": "failed",
                        "message": "找不到文件",
                        "error": f"文件ID不存在: {file_path}"
                    }), 404
                file_path = mapped_path
        
        # 检查是否是任务ID
        task_id = request.args.get('task_id')
        if task_id:
            from file_preview.utils.tasks import get_task_status
            task_status = get_task_status(task_id)
            
            if not task_status or task_status.get('status') != 'completed':
                return jsonify({
                    "status": "processing",
                    "message": "文件转换中，请稍后再试",
                    "task_id": task_id
                })
                
            file_id = task_status.get('file_id')
            if file_id:
                file_mapping = FileMapping(config)
                
                # 获取文件详细信息
                file_info = file_mapping.get_file_info(file_id)
                if file_info:
                    # 尝试获取转换信息
                    converted_info = file_info.get('converted_info')
                    
                    # 如果有转换信息，直接使用转换后的文件路径
                    if converted_info and 'path' in converted_info and os.path.exists(converted_info['path']):
                        logger.info(f"任务ID {task_id} 使用转换文件信息: {converted_info}")
                        file_path = converted_info['path']
                        original_name = file_info.get('original_name')
                    elif 'path' in file_info and os.path.exists(file_info['path']):
                        # 使用文件信息中的路径
                        file_path = file_info['path']
                        original_name = file_info.get('original_name')
                    else:
                        # 回退到基本映射获取
                        mapped_path, original_name = file_mapping.get_by_id(file_id)
                        if mapped_path:
                            file_path = mapped_path
        
        # 如果到这里还没有找到文件，尝试在各个可能的目录中查找
        if not os.path.exists(file_path):
            # 获取项目根目录
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
            
            # 检查几种可能的路径情况
            possible_paths = [
                file_path,  # 原始路径
                os.path.join(root_dir, file_path.lstrip("/")),  # 相对于根目录的路径
                os.path.join(root_dir, config['directories']['download'].lstrip("./"), os.path.basename(file_path)),  # 下载目录
                os.path.join(root_dir, config['directories']['convert'].lstrip("./"), os.path.basename(file_path))   # 转换目录
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
                return jsonify({
                    "status": "failed",
                    "message": "找不到文件",
                    "error": f"文件不存在: {file_path}"
                }), 404
        
        # 获取文件基本信息
        filename = os.path.basename(file_path)
        actual_extension = os.path.splitext(file_path)[1].lower()
        
        # 确定下载的文件名：优先使用转换信息
        if converted_info:
            # 使用转换信息中的文件名
            converted_filename = converted_info.get('filename')
            converted_extension = converted_info.get('extension')
            
            # 如果有原始文件名，结合原始文件名和转换后的扩展名
            if original_name and converted_extension:
                original_basename = os.path.splitext(original_name)[0]
                # 确保扩展名以.开头
                if not converted_extension.startswith('.'):
                    converted_extension = f".{converted_extension}"
                filename = f"{original_basename}{converted_extension}"
                logger.info(f"使用转换信息构建文件名: {filename}")
            elif converted_filename:
                # 直接使用转换后的文件名
                filename = converted_filename
                logger.info(f"使用转换后的文件名: {filename}")
        
        # 如果没有转换信息，使用文件信息和原始文件名推断
        elif is_file_id and file_info:
            # 如果文件信息中有extension字段，优先使用
            if 'extension' in file_info:
                converted_extension = file_info.get('extension', '').lower()
                # 确保扩展名以.开头
                if not converted_extension.startswith('.'):
                    converted_extension = f".{converted_extension}"
                    
                # 如果原始文件名存在
                if original_name:
                    original_basename = os.path.splitext(original_name)[0]
                    original_extension = os.path.splitext(original_name)[1].lower()
                    
                    # 如果原始扩展名和实际文件扩展名不同，使用实际文件扩展名
                    if original_extension != converted_extension:
                        filename = f"{original_basename}{converted_extension}"
                        logger.info(f"使用文件映射中的扩展名: 从 {original_name} 到 {filename}")
                    else:
                        filename = original_name
            # 特殊处理XLS转换为XLSX的情况
            elif original_name:
                original_basename = os.path.splitext(original_name)[0]
                original_extension = os.path.splitext(original_name)[1].lower()
                
                if original_extension == '.xls' and actual_extension == '.xlsx':
                    filename = f"{original_basename}.xlsx"
                    logger.info(f"转换XLS文件名到XLSX: 从 {original_name} 到 {filename}")
                elif original_extension != actual_extension:
                    filename = f"{original_basename}{actual_extension}"
                    logger.info(f"调整下载文件名: 从 {original_name} 到 {filename} 以匹配实际文件类型")
                else:
                    filename = original_name
        
        # 获取文件MIME类型：优先使用转换信息
        if converted_info and 'mime_type' in converted_info:
            mime_type = converted_info['mime_type']
        else:
            # 使用mimetypes库猜测
            mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

        # 仅用于测试：检查是否有test参数，如果有则返回JSON信息而不是文件
        if request.args.get('test') == 'true':
            return jsonify({
                'status': 'success',
                'message': '获取文件信息成功',
                'data': {
                    'file_path': file_path,
                    'mime_type': mime_type,
                    'filename': filename,
                    'original_name': original_name,
                    'file_info': file_info,
                    'converted_info': converted_info,
                    'actual_extension': actual_extension
                }
            })
        
        # 返回文件
        return send_file(
            file_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=filename
        )
            
    except Exception as e:
        logger.error(f"下载文件失败: {str(e)}", exc_info=True)
        return jsonify({
            "status": "failed",
            "message": "下载文件失败",
            "error": str(e)
        }), 500

def get_file_info_api(file_path):
    """获取文件信息API"""
    try:
        # 获取配置
        config = current_app.config['CONFIG']
        
        # 获取项目根目录
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        
        # 检查文件是否存在
        download_dir = os.path.join(root_dir, config['directories']['download'].lstrip("./"))
        file_path = os.path.join(download_dir, file_path)
        
        if not os.path.exists(file_path):
            return jsonify({
                'status': 'failed',
                'message': '文件不存在',
                'error': f'指定的文件不存在 (查找路径: {file_path})'
            }), 404
        
        # 获取文件信息
        file_info = get_file_info(file_path)
        
        return jsonify({
            'status': 'success',
            'message': '获取文件信息成功',
            'data': file_info
        })
        
    except Exception as e:
        return jsonify({
            'status': 'failed',
            'message': '服务器内部错误',
            'error': str(e)
        }), 500 