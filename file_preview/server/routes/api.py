"""
API路由
"""

from flask import Blueprint, request, jsonify, current_app, redirect, url_for
from ..api.converter import convert_file
from ..api.files import get_file_info_api, download_file
from ..api.stats import get_stats
from ..api.converter_status import get_conversion_status
import logging
from file_preview.utils.tasks import conversion_tasks

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/convert', methods=['GET', 'POST'])
def convert():
    """文件转换API"""
    return convert_file(request)

@api_bp.route('/convert/status', methods=['GET', 'POST'])
def conversion_status():
    """任务状态API"""
    # 从查询参数获取任务ID
    task_id = request.args.get('task_id')
    if not task_id:
        return jsonify({
            "status": "failed",
            "message": "缺少必要参数",
            "error": "缺少task_id参数"
        }), 400
        
    # 添加日志记录
    logger = logging.getLogger('file_preview')
    logger.info(f"获取任务状态: {task_id}, 任务列表: {list(conversion_tasks.keys())}")
    
    return get_conversion_status(task_id)

@api_bp.route('/download', methods=['GET', 'POST'])
def download():
    """文件下载API"""
    # 从查询参数获取文件路径
    file_path = request.args.get('file_path') if request.method == 'GET' else request.form.get('file_path')
    file_id = request.args.get('file_id') if request.method == 'GET' else request.form.get('file_id')
    
    # 如果提供了文件ID，优先使用文件ID
    if file_id:
        return download_file(file_id, is_file_id=True)
    
    # 否则使用文件路径
    if not file_path:
        return jsonify({
            "status": "failed",
            "message": "缺少必要参数",
            "error": "缺少file_path或file_id参数"
        }), 400
    return download_file(file_path)

@api_bp.route('/files', methods=['GET', 'POST'])
def file_info():
    """文件信息API"""
    # 从查询参数获取文件ID
    file_id = request.args.get('file_id') if request.method == 'GET' else request.form.get('file_id')
    if not file_id:
        return jsonify({
            "status": "failed",
            "message": "缺少必要参数",
            "error": "缺少file_id参数"
        }), 400
    return get_file_info_api(file_id)

@api_bp.route('/stats', methods=['GET', 'POST'])
def stats():
    """统计信息API"""
    return get_stats() 