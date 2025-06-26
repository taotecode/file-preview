"""
文件预览视图
"""

from flask import render_template_string, jsonify, redirect, current_app, send_file
import os
import logging
from file_preview.utils.mapping import FileMapping
from file_preview.server.views.templates import EXCEL_PREVIEW_TEMPLATE, PREVIEW_TEMPLATE, LOADING_TEMPLATE
from file_preview.utils.file_utils import get_file_info, get_file_md5

logger = logging.getLogger('file_preview')

# 支持的文件类型常量
DOCUMENT_EXTENSIONS = ['.doc', '.docx', '.txt', '.rtf', '.ppt', '.pptx']
SPREADSHEET_EXTENSIONS = ['.xls', '.xlsx']

def render_preview(file_id=None, filename=None, url=None, config=None, convert_to_pdf=False):
    """
    渲染文件预览
    
    Args:
        file_id: 文件ID
        filename: 文件名
        url: 文件URL
        config: 配置信息
        convert_to_pdf: 是否转换为PDF
        
    Returns:
        预览页面或错误响应
    """
    # 创建文件映射实例
    file_mapping = FileMapping(config)
    
    # 根据文件ID预览
    if file_id:
        return _preview_by_file_id(file_id, file_mapping, config, convert_to_pdf)
        
    # 根据URL预览
    elif url:
        return _preview_by_url(url, file_mapping, config, convert_to_pdf)
        
    # 根据文件名预览
    elif filename:
        return _preview_by_filename(filename, file_mapping, config, convert_to_pdf)
        
    # 缺少参数
    else:
        return jsonify({
            'status': 'failed',
            'message': '缺少必要参数',
            'error': '缺少file_id、file或url参数'
        }), 400

def _preview_by_file_id(file_id, file_mapping, config, convert_to_pdf=False):
    """根据文件ID预览文件"""
    # 获取文件路径和原始文件名
    file_path, original_name = file_mapping.get_by_id(file_id)
    
    if not file_path:
        return jsonify({
            'status': 'failed',
            'message': '找不到文件',
            'error': f'文件ID: {file_id} 不存在映射关系'
        }), 404
            
    # 确认文件存在
    if not os.path.exists(file_path):
        file_path = _find_alternative_path(file_path, config)
        if not file_path:
            return jsonify({
                'status': 'failed',
                'message': '找不到文件',
                'error': f'文件不存在'
            }), 404
    
    # 获取文件类型信息
    file_info = get_file_info(file_path)
    file_ext = file_info.get('extension', '').lower()
    
    # 根据文件类型处理预览
    if file_ext in SPREADSHEET_EXTENSIONS and not convert_to_pdf:
        # Excel文件直接预览
        return render_template_string(
            EXCEL_PREVIEW_TEMPLATE,
            title=original_name or os.path.basename(file_path),
            filePath=f"/api/download?file_id={file_id}",
            fileType="excel",
            fileName=original_name or os.path.basename(file_path)
        )
    elif file_ext == '.pdf':
        # PDF直接预览
        return render_template_string(
            PREVIEW_TEMPLATE,
            title=original_name or os.path.basename(file_path),
            pdf_url=f'/view/{file_id}'
        )
    elif file_ext in DOCUMENT_EXTENSIONS or convert_to_pdf:
        # 检查是否已有对应的PDF文件
        pdf_path = _get_pdf_path(file_path, config)
        if pdf_path and os.path.exists(pdf_path):
            # 如果已有PDF文件，创建PDF文件ID并预览
            pdf_file_id = _ensure_file_id(pdf_path, file_mapping, f"{original_name}.pdf" if original_name else None)
            return render_template_string(
                PREVIEW_TEMPLATE,
                title=original_name or os.path.basename(file_path),
                pdf_url=f'/view/{pdf_file_id}'
            )
        else:
            # 否则创建转换任务
            from ..api.converter import create_conversion_task
            task_id = create_conversion_task(file_id=file_id, config=config, convert_to_pdf=True)
            return render_template_string(
                LOADING_TEMPLATE,
                task_id=task_id
            )
    else:
        # 不支持的文件类型
        return jsonify({
            'status': 'failed',
            'message': '不支持的文件类型预览',
            'error': f'不支持预览文件类型: {file_ext}'
        }), 400

def _preview_by_url(url, file_mapping, config, convert_to_pdf=False):
    """根据URL预览文件"""
    # 检查URL是否已经处理过
    file_id = file_mapping.get_id_by_url(url)
    if file_id:
        # URL已处理过，获取文件信息
        file_path, original_name = file_mapping.get_by_id(file_id)
        if file_path and os.path.exists(file_path):
            # 更新访问时间
            file_mapping.update_access_time(file_id)
            # 根据已有文件ID进行预览
            return _preview_by_file_id(file_id, file_mapping, config, convert_to_pdf)
    
    # URL未处理过，创建转换任务
    from ..api.converter import create_conversion_task
    task_id = create_conversion_task(url=url, config=config, convert_to_pdf=convert_to_pdf)
    return render_template_string(
        LOADING_TEMPLATE,
        task_id=task_id
    )

def _preview_by_filename(filename, file_mapping, config, convert_to_pdf=False):
    """根据文件名预览文件"""
    # 获取文件路径
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    convert_dir = os.path.join(root_dir, config['directories']['convert'].lstrip("./"))
    download_dir = os.path.join(root_dir, config['directories']['download'].lstrip("./"))
    
    file_path = os.path.join(convert_dir, filename)
    download_path = os.path.join(download_dir, filename)
    
    # 检查文件类型
    file_info = get_file_info(filename)
    file_ext = file_info.get('extension', '').lower()
    
    # 检查文件是否存在
    if os.path.exists(download_path):
        target_path = download_path
    elif os.path.exists(file_path):
        target_path = file_path
    else:
        if convert_to_pdf:
            # 如果需要转换为PDF但文件不存在，重定向到转换API
            return redirect(f"/api/convert?file={filename}&convert_to_pdf=true")
        else:
            return jsonify({
                'status': 'failed',
                'message': '找不到文件',
                'error': f'文件不存在: {filename}'
            }), 404
    
    # 获取或创建文件ID
    file_id = _ensure_file_id(target_path, file_mapping, filename)
    
    # 根据文件ID进行预览
    return _preview_by_file_id(file_id, file_mapping, config, convert_to_pdf)

def _find_alternative_path(file_path, config):
    """查找替代文件路径"""
    # 获取项目根目录
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    
    # 尝试几种可能的路径
    possible_paths = [
        file_path,  # 原始路径
        os.path.join(root_dir, file_path.lstrip("/")),  # 相对于根目录的路径
        os.path.join(root_dir, config['directories']['convert'].lstrip("./"), os.path.basename(file_path)),  # 转换目录
        os.path.join(root_dir, config['directories']['download'].lstrip("./"), os.path.basename(file_path))   # 下载目录
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"找到替代文件路径: {path}")
            return path
    
    return None

def _get_pdf_path(file_path, config):
    """获取对应的PDF文件路径"""
    # 获取项目根目录和转换目录
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    convert_dir = os.path.join(root_dir, config['directories']['convert'].lstrip("./"))
    
    # 生成PDF文件路径
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    pdf_path = os.path.join(convert_dir, f"{base_name}.pdf")
    
    return pdf_path

def _ensure_file_id(file_path, file_mapping, original_name=None):
    """确保文件有对应的ID"""
    file_md5 = get_file_md5(file_path)
    
    # 获取或创建文件ID
    file_id = file_mapping.get_id_by_md5(file_md5)
    if not file_id:
        file_id = file_mapping.add(file_md5, file_path, original_name or os.path.basename(file_path))
    else:
        # 更新访问时间
        file_mapping.update_access_time(file_md5)
    
    return file_id

def preview_file(file_id):
    """通过文件ID预览文件的入口函数"""
    try:
        # 获取配置
        config = current_app.config.get('CONFIG')
        if not config:
            return jsonify({
                'status': 'failed',
                'message': '服务器配置错误',
                'error': '无法访问配置信息'
            }), 500
        
        # 创建文件映射实例
        file_mapping = FileMapping(config)
        
        # 通过辅助函数预览文件
        return _preview_by_file_id(file_id, file_mapping, config)
    
    except Exception as e:
        logger.error(f"预览文件失败: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'failed',
            'message': '预览文件失败',
            'error': str(e)
        }), 500

def direct_view_file(file_id):
    """直接预览文件（不使用模板）"""
    try:
        # 获取配置
        config = current_app.config.get('CONFIG')
        if not config:
            logger.error(f"无法访问配置信息，file_id: {file_id}")
            return jsonify({
                'status': 'failed',
                'message': '服务器配置错误',
                'error': '无法访问配置信息'
            }), 500
        
        # 创建文件映射实例
        file_mapping = FileMapping(config)
        
        # 获取文件路径
        file_path, original_name = file_mapping.get_by_id(file_id)
        if not file_path:
            logger.error(f"找不到文件ID: {file_id}的映射")
            return jsonify({
                'status': 'failed',
                'message': '找不到文件',
                'error': f'文件ID: {file_id} 不存在映射关系'
            }), 404
            
        # 确认文件存在
        if not os.path.exists(file_path):
            file_path = _find_alternative_path(file_path, config)
            if not file_path:
                return jsonify({
                    'status': 'failed',
                    'message': '找不到文件',
                    'error': f'文件不存在'
                }), 404
        
        # 获取文件类型
        file_info = get_file_info(file_path)
        file_ext = file_info.get('extension', '').lower()
        
        # 检查是否存在转换后的PDF文件
        if file_ext != '.pdf' and file_ext in DOCUMENT_EXTENSIONS:
            pdf_path = _get_pdf_path(file_path, config)
            if os.path.exists(pdf_path):
                logger.info(f"使用转换后的PDF文件: {pdf_path}")
                return send_file(pdf_path, as_attachment=False)
        
        # 直接发送文件，确保在浏览器中预览而不是下载
        return send_file(file_path, as_attachment=False)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"预览文件失败: {str(e)}\n{error_trace}")
        return jsonify({
            'status': 'failed',
            'message': '预览文件失败',
            'error': str(e)
        }), 500 