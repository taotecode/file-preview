"""
文件上传视图
"""

from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from file_preview.utils.file_utils import is_supported_file, save_uploaded_file
from file_preview.utils.file_processor import FileProcessor

def upload_file():
    """处理文件上传"""
    try:
        # 获取配置
        config = current_app.config['CONFIG']
        
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('没有选择文件')
                return redirect(request.url)
                
            file = request.files['file']
            if file.filename == '':
                flash('没有选择文件')
                return redirect(request.url)
                
            if not is_supported_file(file.filename):
                flash('不支持的文件类型')
                return redirect(request.url)
                
            # 保存文件
            filename = secure_filename(file.filename)
            file_path = save_uploaded_file(file, filename)
            
            try:
                # 使用 FileProcessor 处理文件转换
                file_processor = FileProcessor(config)
                response = file_processor.process_file(file_path, None, filename)
                
                if response["status"] == "success":
                    return jsonify({
                        'status': 'success',
                        'message': '文件上传成功',
                        'task_id': response["task_id"],
                        'file_id': response["file_id"],
                        'file_name': filename,
                        'preview_url': response.get("preview_url"),
                        'download_url': response.get("download_url")
                    })
                else:
                    # 删除上传的文件
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    return jsonify({
                        'status': 'failed',
                        'message': '文件处理失败',
                        'error': response.get("error", "未知错误")
                    }), 500
                
            except Exception as e:
                # 删除上传的文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise e
                
        return render_template('upload.html')
        
    except Exception as e:
        return jsonify({
            'status': 'failed',
            'message': '文件上传失败',
            'error': str(e)
        }), 500 