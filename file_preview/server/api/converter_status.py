"""
转换状态API
"""

from flask import jsonify, current_app, request
from file_preview.utils.tasks import get_task_status, conversion_tasks
import os
import logging

# 获取日志记录器
logger = logging.getLogger('file_preview')

def get_conversion_status(task_id):
    """
    获取转换状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        状态响应
    """
    try:
        # 获取配置
        config = current_app.config['CONFIG']
        
        # 获取任务状态
        task_status = get_task_status(task_id)
        
        # 输出调试信息
        logger.debug(f"任务状态: {task_status}, 所有任务: {conversion_tasks}")
        
        # 任务不存在
        if task_status is None:
            return jsonify({
                "status": "failed",
                "message": "任务不存在",
                "error": "找不到指定的任务ID"
            }), 404
            
        # 任务正在处理中
        if task_status.get('status') == 'processing':
            return jsonify({
                "status": "processing",
                "message": "任务正在处理中",
                "progress": task_status.get('progress', 0)
            })
            
        # 任务失败
        elif task_status.get('status') == 'failed':
            return jsonify({
                "status": "failed",
                "message": "处理失败",
                "error": task_status.get('error', '未知错误')
            })
            
        # 任务完成
        elif task_status.get('status') == 'completed':
            # 获取任务中可能已经包含的信息
            filename = task_status.get('filename', '')
            file_id = task_status.get('file_id', '')
            download_url = task_status.get('download_url', '')
            preview_url = task_status.get('preview_url', '')
            
            # 如果没有下载URL，则根据文件ID或文件名生成
            if not download_url:
                if file_id:
                    download_url = f"/api/files/download?file_id={file_id}"
                elif filename:
                    download_url = f"/api/download?file_path={filename}"
            
            # 如果没有预览URL，则根据文件ID或文件名生成
            if not preview_url:
                if file_id:
                    preview_url = f"/preview?file_id={file_id}"
                elif filename:
                    preview_url = f"/preview?file={filename}"
                
            return jsonify({
                "status": "success",
                "message": task_status.get('message', "处理完成"),
                "filename": filename,
                "file_id": file_id,
                "download_url": download_url,
                "preview_url": preview_url
            })
            
        # 未知状态
        else:
            return jsonify({
                "status": "unknown",
                "message": "未知状态",
                "task_status": task_status
            })
            
    except Exception as e:
        logger.error(f"获取转换状态失败: {str(e)}", exc_info=True)
        return jsonify({
            "status": "failed",
            "message": "获取状态失败",
            "error": str(e)
        }), 500 