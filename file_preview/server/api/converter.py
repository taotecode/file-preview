"""
文件转换API
"""

from flask import request, jsonify, current_app
from typing import Dict, Any
from file_preview.utils.tasks import (
    process_file_conversion, download_and_process_url, 
    check_mapped_file, create_task_id, start_background_task,
    process_task, conversion_tasks, create_conversion_task
)
from file_preview.utils.file_utils import is_supported_format, get_file_md5, get_url_md5
from file_preview.core.cache import CacheManager
from file_preview.utils.mapping import FileMapping
from file_preview.utils.file_processor import FileProcessor
import os
from werkzeug.utils import secure_filename
import logging
import traceback
import time
import json
from file_preview.utils.response import generate_error_response
from file_preview.utils.utils import get_string_md5

logger = logging.getLogger("file_preview")

def convert_file(request):
    """文件转换API"""
    # 获取应用配置
    config = current_app.config['CONFIG']
    
    # 提取请求参数
    file_id = request.args.get('file_id') if request.method == 'GET' else request.form.get('file_id')
    file_path = request.args.get('file') if request.method == 'GET' else request.form.get('file')
    url = request.args.get('url') if request.method == 'GET' else request.form.get('url')
    
    # 检查是否提供了必要参数
    if not file_id and not file_path and not url and not request.files:
        return jsonify({
            'status': 'failed',
            'message': '缺少必要参数',
            'error': '必须提供file、file_id、url或上传文件'
        }), 400
    
    # 创建FileProcessor实例
    file_processor = FileProcessor(config)
    
    # 初始化任务ID，响应和文件ID
    task_id = None
    response = None
    file_mapping = FileMapping(config)
    
    # 处理不同类型的请求
    try:
        if url:
            # 处理URL请求
            url_md5 = get_url_md5(url)
            
            # 检查是否已存在相同URL的处理结果
            existing_file_id = file_mapping.get_id_by_url(url) or file_mapping.get_id_by_md5(url_md5)
            
            if existing_file_id:
                # 检查文件是否存在
                file_info = file_mapping.get_file_info(existing_file_id)
                if file_info and os.path.exists(file_info.get('path', '')):
                    # 已存在处理结果，直接使用
                    logger.info(f"URL已有处理结果: {url} -> {existing_file_id}")
                    
                    # 创建任务ID
                    task_id = create_task_id()
                    
                    # 更新任务状态为已完成
                    conversion_tasks[task_id] = {
                        'status': 'completed',
                        'message': '文件处理完成',
                        'file_id': existing_file_id,
                        'download_url': f"/api/download?file_id={existing_file_id}",
                        'preview_url': f"/preview?file_id={existing_file_id}"
                    }

            else:
                # 创建任务ID
                task_id = create_task_id()
                logger.info(f"创建URL处理任务: {task_id} 处理URL: {url}")
                
                # 开始后台任务处理URL
                start_background_task(_process_url, task_id, url, config)
            
                # 添加任务状态
                conversion_tasks[task_id] = {
                    'status': 'processing',
                    'message': '正在处理URL',
                    'url': url,
                    'url_md5': url_md5,
                    'file_id': existing_file_id
                }
            
        elif file_path and os.path.exists(file_path):
            # 处理本地文件
            file_md5 = get_file_md5(file_path)
            
            # 直接处理文件
            response = file_processor.process_file(file_path, file_md5)
            task_id = response.get('task_id')
            
            # 更新任务状态
            if response["status"] == "success":
                conversion_tasks[task_id] = {
                    'status': 'completed',
                    'message': '文件处理完成',
                    'file_id': response.get('file_id'),
                    'preview_url': response.get('preview_url'),
                    'download_url': response.get('download_url')
                }
            else:
                conversion_tasks[task_id] = {
                    'status': 'failed',
                    'error': response.get('error', '处理失败')
                }
                
        elif file_id:
            # 处理文件ID请求
            # 检查文件是否已经处理过
            file_info = file_mapping.get_info_by_id(file_id)
            
            if file_info and os.path.exists(file_info.get('path')):
                # 文件已存在，直接返回信息
                task_id = create_task_id()
                conversion_tasks[task_id] = {
                    'status': 'completed',
                    'message': '文件已存在',
                    'file_id': file_id,
                    'preview_url': f"/preview?file_id={file_id}",
                    'download_url': f"/api/download?file_id={file_id}"
                }
            else:
                # 文件ID无效
                return jsonify({
                    'status': 'failed',
                    'message': '无效的文件ID',
                    'error': f'找不到ID为 {file_id} 的文件'
                }), 404
                
        elif request.files.get('file'):
            # 处理上传的文件
            uploaded_file = request.files['file']
            filename = secure_filename(uploaded_file.filename)
            
            # 确保上传目录存在
            upload_dir = config['directories']['upload']
            os.makedirs(upload_dir, exist_ok=True)
            
            # 保存上传的文件
            file_path = os.path.join(upload_dir, filename)
            uploaded_file.save(file_path)
            
            # 处理文件
            response = file_processor.process_file(file_path, None, filename)
            task_id = response.get('task_id')
            
            # 更新任务状态
            if response["status"] == "success":
                conversion_tasks[task_id] = {
                    'status': 'completed',
                    'message': '文件处理完成',
                    'file_id': response.get('file_id'),
                    'preview_url': response.get('preview_url'),
                    'download_url': response.get('download_url')
                }
            else:
                conversion_tasks[task_id] = {
                    'status': 'failed',
                    'error': response.get('error', '处理失败')
                }
    except Exception as e:
        logger.error(f"处理文件请求失败: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'failed',
            'message': '处理请求失败',
            'error': str(e)
        }), 500
    
    # 获取任务状态
    task_status = conversion_tasks.get(task_id, {})
    
    # 如果任务已完成，返回完整信息
    if task_status.get('status') == 'completed':
        return jsonify({
            'status': 'success',
            'message': '文件处理完成',
            'task_id': task_id,
            'file_id': task_status.get('file_id'),
            'preview_url': task_status.get('preview_url'),
            'download_url': task_status.get('download_url')
        })
    
    # 构建预期的URLs（即使文件还在处理中）
    response_data = {
        'status': 'processing',
        'message': '文件正在处理中',
        'task_id': task_id
    }
    
    # 添加文件ID（如果已知）
    if task_status.get('file_id'):
        response_data['file_id'] = task_status.get('file_id')
        response_data['preview_url'] = f"/preview?file_id={response_data['file_id']}"
        response_data['download_url'] = f"/api/files/download?file_id={response_data['file_id']}"
    
    return jsonify(response_data)

def _process_url(task_id: str, url: str, config: Dict[str, Any]) -> None:
    """处理URL的后台任务"""
    try:
        # 创建文件处理器
        file_processor = FileProcessor(config)
        
        # 处理URL
        response = file_processor.process_url(url)
        
        # 更新任务状态
        if response["status"] == "success":
            # 获取更详细的文件信息
            file_mapping = FileMapping(config)
            file_id = response.get('file_id')
            file_info = None
            
            if file_id:
                file_info = file_mapping.get_file_info(file_id)
            
            # 构建更完整的任务信息
            task_info = {
                'status': 'completed',
                'message': '文件处理完成',
                'file_id': file_id,
                'preview_url': response.get('preview_url'),
                'download_url': response.get('download_url')
            }
            
            # 添加文件详细信息
            if file_info:
                task_info['file_info'] = file_info
            
            # 添加原始文件信息
            if 'original_file_info' in response:
                task_info['original_file_info'] = response['original_file_info']
            
            # 添加转换文件信息
            if 'converted_file_info' in response:
                task_info['converted_file_info'] = response['converted_file_info']
                
            # 添加其他响应信息
            if 'filename' in response:
                task_info['filename'] = response['filename']
            if 'original_name' in response:
                task_info['original_name'] = response['original_name']
                
            # 更新任务状态
            conversion_tasks[task_id] = task_info
        else:
            conversion_tasks[task_id] = {
                'status': 'failed',
                'error': response.get('error', '处理失败')
            }
    
    except Exception as e:
        logger.error(f"处理URL失败: {str(e)}", exc_info=True)
        conversion_tasks[task_id] = {
            'status': 'failed',
            'message': '处理URL失败',
            'error': str(e)
        }

def process_url(request):
    """
    处理URL
    
    Args:
        request: Flask请求对象
        
    Returns:
        处理结果
    """
    try:
        # 获取URL
        url = request.args.get('url') if request.method == 'GET' else request.form.get('url')
        
        if not url:
            return jsonify({
                "status": "failed",
                "message": "缺少必要参数",
                "error": "缺少url参数"
            }), 400
            
        # 获取配置
        config = current_app.config['CONFIG']
        
        # 创建任务ID 
        task_id = create_task_id()
        logger.info(f"创建URL处理任务: {task_id} 处理URL: {url}")
        
        # 检查是否已存在相同URL的处理结果
        file_mapping = FileMapping(config)
        existing_file_id = file_mapping.get_id_by_url(url)
        
        if existing_file_id:
            # 检查文件是否存在
            file_info = file_mapping.get_file_info(existing_file_id)
            if file_info and os.path.exists(file_info.get('path', '')):
                # 已存在处理结果，直接返回
                logger.info(f"URL已有处理结果: {url} -> {existing_file_id}")
                
                # 更新任务状态为已完成
                conversion_tasks[task_id] = {
                    'status': 'completed',
                    'message': '文件处理完成',
                    'file_id': existing_file_id,
                    'download_url': f"/api/files/download?file_id={existing_file_id}",
                    'preview_url': f"/preview?file_id={existing_file_id}"
                }
                
                # 返回处理中状态，让前端轮询查询
                return jsonify({
                    "status": "processing",
                    "message": "文件正在处理中",
                    "task_id": task_id
                })
        
        # 创建处理器实例
        file_processor = FileProcessor(config)
        
        # 处理URL，获取转换后的文件信息
        task_id = create_task_id()
        
        # 开始后台任务处理URL
        start_background_task(_process_url, task_id, url, config)
        
        # 添加初始任务状态
        url_md5 = get_url_md5(url)
        file_mapping = FileMapping(config)
        existing_file_id = file_mapping.get_id_by_url(url) or file_mapping.get_id_by_md5(url_md5)
        
        conversion_tasks[task_id] = {
            'status': 'processing',
            'message': '正在处理URL',
            'url': url,
            'url_md5': url_md5,
            'file_id': existing_file_id
        }
        
        # 构建响应
        response_data = {
            'status': 'processing',
            'message': '文件正在处理中',
            'task_id': task_id
        }
        
        # 添加文件ID（如果已知）
        if existing_file_id:
            response_data['file_id'] = existing_file_id
            response_data['preview_url'] = f"/preview?file_id={existing_file_id}"
            response_data['download_url'] = f"/api/files/download?file_id={existing_file_id}"
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"处理URL失败: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'failed',
            'message': '处理URL失败',
            'error': str(e)
        }), 500

# 为了内部使用，保留process_url函数，但不再作为别名导出
# convert_url = process_url 