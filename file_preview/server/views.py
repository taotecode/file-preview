"""
视图模板
"""

# 加载动画 HTML 模板
LOADING_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>文件转换中...</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f5f5f5;
        }
        .loading-container {
            text-align: center;
        }
        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .message {
            color: #333;
            font-size: 18px;
        }
    </style>
    <script>
        function checkStatus() {
            fetch('/api/convert/status/{{ task_id }}')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'completed') {
                        window.location.href = '/api/preview/' + data.filename;
                    } else if (data.status === 'failed') {
                        document.querySelector('.message').textContent = '转换失败: ' + data.error;
                    } else {
                        setTimeout(checkStatus, 1000);
                    }
                })
                .catch(error => {
                    document.querySelector('.message').textContent = '发生错误: ' + error;
                });
        }
        window.onload = function() {
            checkStatus();
        };
    </script>
</head>
<body>
    <div class="loading-container">
        <div class="spinner"></div>
        <div class="message">加载中，请稍候...</div>
    </div>
</body>
</html>
"""

# 预览页面 HTML 模板
PREVIEW_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        object {
            width: 100%;
            height: 100vh;
            border: none;
        }
    </style>
</head>
<body>
    <object data="{{ pdf_url }}" type="application/pdf">
        <p>无法显示 PDF 文件，请 <a href="{{ pdf_url }}">下载</a> 后查看</p>
    </object>
</body>
</html>
""" 