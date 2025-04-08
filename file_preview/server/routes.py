"""
API 路由
"""

import os
import logging
from flask import Blueprint, request, jsonify, send_file, abort, current_app, render_template_string
from werkzeug.utils import secure_filename
from typing import Dict, Any
from ..core.converter import FileConverter
from ..core.downloader import FileDownloader
from ..core.cache import CacheManager
from ..utils.file import get_file_info, is_supported_format, get_file_md5, get_url_md5, generate_output_path
from ..utils.mapping import FileMapping
from .views import LOADING_TEMPLATE, PREVIEW_TEMPLATE

# 创建蓝图
api_bp = Blueprint('api', __name__)

# 获取日志记录器
logger = logging.getLogger('file_preview')

# 存储转换任务状态
conversion_tasks = {}

@api_bp.route('/api/convert', methods=['POST'])
def convert_file():
    """
    转换上传的文件
    """
    try:
        # 获取配置
        config = current_app.config['CONFIG']
        
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 检查文件类型
        if not is_supported_format(file.filename, config):
            return jsonify({'error': '不支持的文件类型'}), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # 计算文件 MD5
            file_md5 = get_file_md5(file_path)
            
            # 检查文件映射
            file_mapping = FileMapping(config)
            mapped_pdf = file_mapping.get(file_md5)
            if mapped_pdf:
                # 生成任务 ID
                task_id = os.urandom(16).hex()
                conversion_tasks[task_id] = {
                    'status': 'completed',
                    'filename': os.path.basename(mapped_pdf)
                }
                return render_template_string(LOADING_TEMPLATE, task_id=task_id)
            
            # 生成任务 ID
            task_id = os.urandom(16).hex()
            
            # 初始化任务状态
            conversion_tasks[task_id] = {
                'status': 'processing',
                'filename': None,
                'error': None
            }
            
            # 启动后台任务
            def process_file():
                try:
                    # 转换文件
                    converter = FileConverter(config)
                    cache_manager = CacheManager(config)
                    
                    # 检查缓存
                    if cache_manager.exists(file_path):
                        pdf_path = cache_manager.get(file_path)
                    else:
                        pdf_path = converter.convert(file_path)
                        if not pdf_path:
                            conversion_tasks[task_id]['status'] = 'failed'
                            conversion_tasks[task_id]['error'] = '转换失败'
                            return
                        
                        # 添加到缓存
                        cache_manager.put(file_path, pdf_path)
                    
                    # 添加文件映射
                    file_mapping.add(file_md5, pdf_path, filename)
                    
                    # 更新任务状态
                    conversion_tasks[task_id]['status'] = 'completed'
                    conversion_tasks[task_id]['filename'] = os.path.basename(pdf_path)
                    
                except Exception as e:
                    conversion_tasks[task_id]['status'] = 'failed'
                    conversion_tasks[task_id]['error'] = str(e)
            
            # 在后台线程中处理文件
            import threading
            thread = threading.Thread(target=process_file)
            thread.start()
            
            # 返回加载页面
            return render_template_string(LOADING_TEMPLATE, task_id=task_id)
            
        finally:
            # 删除上传的临时文件
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        logger.error(f"转换文件失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@api_bp.route('/api/convert/url', methods=['GET'])
def convert_url():
    """
    转换 URL 文件
    """
    try:
        # 获取配置
        config = current_app.config['CONFIG']
        
        # 获取 URL 参数
        url = request.args.get('url')
        if not url:
            return jsonify({'error': '缺少 URL 参数'}), 400
        
        # 计算 URL MD5
        url_md5 = get_url_md5(url)
        
        # 检查文件映射
        file_mapping = FileMapping(config)
        mapped_pdf = file_mapping.get(url_md5)
        if mapped_pdf:
            # 生成任务 ID
            task_id = os.urandom(16).hex()
            conversion_tasks[task_id] = {
                'status': 'completed',
                'filename': os.path.basename(mapped_pdf)
            }
            return render_template_string(LOADING_TEMPLATE, task_id=task_id)
        
        # 生成任务 ID
        task_id = os.urandom(16).hex()
        
        # 初始化任务状态
        conversion_tasks[task_id] = {
            'status': 'processing',
            'url': url,
            'url_md5': url_md5,
            'filename': None,
            'error': None
        }
        
        # 启动后台任务
        def process_file():
            try:
                # 下载文件
                downloader = FileDownloader(config)
                file_path = downloader.download(url)
                if not file_path:
                    conversion_tasks[task_id]['status'] = 'failed'
                    conversion_tasks[task_id]['error'] = '下载失败'
                    return
                
                try:
                    # 检查文件类型
                    if not is_supported_format(file_path, config):
                        conversion_tasks[task_id]['status'] = 'failed'
                        conversion_tasks[task_id]['error'] = '不支持的文件类型'
                        return
                    
                    # 转换文件
                    converter = FileConverter(config)
                    cache_manager = CacheManager(config)
                    
                    # 检查缓存
                    if cache_manager.exists(file_path):
                        pdf_path = cache_manager.get(file_path)
                    else:
                        pdf_path = converter.convert(file_path)
                        if not pdf_path:
                            conversion_tasks[task_id]['status'] = 'failed'
                            conversion_tasks[task_id]['error'] = '转换失败'
                            return
                        
                        # 添加到缓存
                        cache_manager.put(file_path, pdf_path)
                    
                    # 添加文件映射
                    file_mapping.add(url_md5, pdf_path, os.path.basename(file_path))
                    
                    # 更新任务状态
                    conversion_tasks[task_id]['status'] = 'completed'
                    conversion_tasks[task_id]['filename'] = os.path.basename(pdf_path)
                    
                finally:
                    # 删除下载的临时文件
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        
            except Exception as e:
                conversion_tasks[task_id]['status'] = 'failed'
                conversion_tasks[task_id]['error'] = str(e)
        
        # 在后台线程中处理文件
        import threading
        thread = threading.Thread(target=process_file)
        thread.start()
        
        # 返回加载页面
        return render_template_string(LOADING_TEMPLATE, task_id=task_id)
                
    except Exception as e:
        logger.error(f"转换 URL 文件失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@api_bp.route('/api/preview/<filename>')
def preview_file(filename: str):
    """
    预览文件
    """
    try:
        # 获取配置
        config = current_app.config['CONFIG']
        
        # 检查文件是否存在
        file_path = os.path.join(config['directories']['convert'], filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        # 获取文件 MD5
        file_md5 = get_file_md5(file_path)
        
        # 更新文件映射访问时间
        file_mapping = FileMapping(config)
        file_mapping.update_access_time(file_md5)
        
        # 获取原始文件名
        original_name = file_mapping.get_original_name(file_md5)
        if not original_name:
            original_name = filename
        
        # 渲染预览页面
        return render_template_string(
            PREVIEW_TEMPLATE,
            title=original_name,
            pdf_url=f'/api/view/{filename}'
        )
        
    except Exception as e:
        logger.error(f"预览文件失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@api_bp.route('/api/view/<filename>')
def view_file(filename: str):
    """
    查看文件
    """
    try:
        # 获取配置
        config = current_app.config['CONFIG']
        
        # 检查文件是否存在
        file_path = os.path.join(config['directories']['convert'], filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        # 获取文件 MD5
        file_md5 = get_file_md5(file_path)
        
        # 更新文件映射访问时间
        file_mapping = FileMapping(config)
        file_mapping.update_access_time(file_md5)
        
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=False
        )
        
    except Exception as e:
        logger.error(f"查看文件失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@api_bp.route('/api/download/<filename>')
def download_file(filename: str):
    """
    下载文件
    """
    try:
        # 获取配置
        config = current_app.config['CONFIG']
        
        # 检查文件是否存在
        file_path = os.path.join(config['directories']['convert'], filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        # 获取文件 MD5
        file_md5 = get_file_md5(file_path)
        
        # 更新文件映射访问时间
        file_mapping = FileMapping(config)
        file_mapping.update_access_time(file_md5)
        
        # 获取原始文件名
        original_name = file_mapping.get_original_name(file_md5)
        if not original_name:
            original_name = filename
        
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=original_name
        )
        
    except Exception as e:
        logger.error(f"下载文件失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@api_bp.route('/api/preview/url', methods=['GET'])
def preview_url():
    """
    预览 URL 文件
    """
    try:
        # 获取配置
        config = current_app.config['CONFIG']
        
        # 获取 URL 参数
        url = request.args.get('url')
        if not url:
            return jsonify({'error': '缺少 URL 参数'}), 400
        
        # 计算 URL MD5
        url_md5 = get_url_md5(url)
        
        # 检查文件映射
        file_mapping = FileMapping(config)
        mapped_pdf = file_mapping.get(url_md5)
        if mapped_pdf:
            # 生成任务 ID
            task_id = os.urandom(16).hex()
            conversion_tasks[task_id] = {
                'status': 'completed',
                'filename': os.path.basename(mapped_pdf)
            }
            return render_template_string(LOADING_TEMPLATE, task_id=task_id)
        
        # 生成任务 ID
        task_id = os.urandom(16).hex()
        
        # 初始化任务状态
        conversion_tasks[task_id] = {
            'status': 'processing',
            'url': url,
            'url_md5': url_md5,
            'filename': None,
            'error': None
        }
        
        # 启动后台任务
        def process_file():
            try:
                # 下载文件
                downloader = FileDownloader(config)
                file_path = downloader.download(url)
                if not file_path:
                    conversion_tasks[task_id]['status'] = 'failed'
                    conversion_tasks[task_id]['error'] = '下载失败'
                    return
                
                try:
                    # 检查文件类型
                    if not is_supported_format(file_path, config):
                        conversion_tasks[task_id]['status'] = 'failed'
                        conversion_tasks[task_id]['error'] = '不支持的文件类型'
                        return
                    
                    # 转换文件
                    converter = FileConverter(config)
                    cache_manager = CacheManager(config)
                    
                    # 检查缓存
                    if cache_manager.exists(file_path):
                        pdf_path = cache_manager.get(file_path)
                    else:
                        pdf_path = converter.convert(file_path)
                        if not pdf_path:
                            conversion_tasks[task_id]['status'] = 'failed'
                            conversion_tasks[task_id]['error'] = '转换失败'
                            return
                        
                        # 添加到缓存
                        cache_manager.put(file_path, pdf_path)
                    
                    # 添加文件映射
                    file_mapping.add(url_md5, pdf_path, os.path.basename(file_path))
                    
                    # 更新任务状态
                    conversion_tasks[task_id]['status'] = 'completed'
                    conversion_tasks[task_id]['filename'] = os.path.basename(pdf_path)
                    
                finally:
                    # 删除下载的临时文件
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        
            except Exception as e:
                conversion_tasks[task_id]['status'] = 'failed'
                conversion_tasks[task_id]['error'] = str(e)
        
        # 在后台线程中处理文件
        import threading
        thread = threading.Thread(target=process_file)
        thread.start()
        
        # 返回加载页面
        return render_template_string(LOADING_TEMPLATE, task_id=task_id)
                
    except Exception as e:
        logger.error(f"预览 URL 文件失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@api_bp.route('/api/convert/status/<task_id>')
def check_conversion_status(task_id: str):
    """
    检查转换状态
    """
    if task_id not in conversion_tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    task = conversion_tasks[task_id]
    return jsonify(task) 