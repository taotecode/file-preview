"""
页面渲染路由
"""

from flask import Blueprint, request, redirect, current_app, jsonify, render_template_string, send_file, url_for
from ..views.preview import render_preview, preview_file, direct_view_file
from ..views.templates import LOADING_TEMPLATE
import os
import logging

logger = logging.getLogger('file_preview')

# 创建视图蓝图
views_bp = Blueprint('views', __name__)

@views_bp.route('/preview', methods=['GET', 'POST'])
def preview():
    """预览文件API"""
    # 获取参数
    if request.method == 'GET':
        file_id = request.args.get('file_id')
        filename = request.args.get('file')
        url = request.args.get('url')
        task_id = request.args.get('task_id')
        convert_to_pdf = request.args.get('convert_to_pdf', 'false').lower() == 'true'
        direct_view = request.args.get('direct_view', 'false').lower() == 'true'
    else:  # POST
        file_id = request.form.get('file_id')
        filename = request.form.get('file')
        url = request.form.get('url')
        task_id = request.form.get('task_id')
        convert_to_pdf = request.form.get('convert_to_pdf', 'false').lower() == 'true'
        direct_view = request.form.get('direct_view', 'false').lower() == 'true'
    
    # 获取配置
    config = current_app.config['CONFIG']
    
    # 如果提供了task_id，显示加载页面
    if task_id:
        return render_template_string(
            LOADING_TEMPLATE,
            task_id=task_id
        )
        
    # 如果提供了file_id，尝试直接预览
    if file_id:
        # 如果direct_view参数为true，使用直接预览功能
        if direct_view:
            return direct_view_file(file_id)
        else:
            return preview_file(file_id)
        
    # 处理文件名或URL
    return render_preview(file_id, filename, url, config, convert_to_pdf)

@views_bp.route('/view/<file_id>', methods=['GET'])
def view_file(file_id):
    """直接查看文件（无需模板包装的原始文件）"""
    return direct_view_file(file_id)

def direct_view_file(file_id):
    """实现直接预览文件功能（从旧的view_file路由移植过来）"""
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
        
        # 获取项目根目录
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        
        # 获取文件映射
        from file_preview.utils.mapping import FileMapping
        file_mapping = FileMapping(config)
        file_path, original_name = file_mapping.get_by_id(file_id)
        
        if not file_path:
            logger.error(f"找不到文件ID: {file_id}的映射")
            return jsonify({
                'status': 'failed',
                'message': '找不到文件',
                'error': f'文件ID: {file_id} 不存在映射关系'
            }), 404
            
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            
            # 尝试查找其他可能的路径
            possible_paths = [
                file_path,  # 原始路径
                os.path.join(root_dir, file_path.lstrip("/")),  # 相对于根目录的路径
                os.path.join(root_dir, config['directories']['convert'].lstrip("./"), os.path.basename(file_path)),  # 转换目录
                os.path.join(root_dir, config['directories']['download'].lstrip("./"), os.path.basename(file_path))   # 下载目录
            ]
            
            file_found = False
            for possible_path in possible_paths:
                if os.path.exists(possible_path):
                    file_path = possible_path
                    file_found = True
                    logger.info(f"找到替代文件路径: {file_path}")
                    break
            
            if not file_found:
                return jsonify({
                    'status': 'failed',
                    'message': '找不到文件',
                    'error': f'文件不存在: {file_path}'
                }), 404
        
        # 获取文件类型
        from file_preview.utils.file_utils import get_file_info
        file_info = get_file_info(file_path)
        file_ext = file_info.get('extension', '').lower()
        
        # 检查是否存在转换后的PDF文件
        pdf_file_path = f"{os.path.splitext(file_path)[0]}.pdf"
        if file_ext != '.pdf' and os.path.exists(pdf_file_path):
            # 如果存在PDF版本，优先使用PDF
            logger.info(f"使用转换后的PDF文件: {pdf_file_path}")
            return send_file(pdf_file_path, as_attachment=False)
        
        # 直接发送文件，设置 as_attachment=False 确保在浏览器中预览而不是下载
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