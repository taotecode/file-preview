# API 文档

## 概述

文件预览工具提供了一组 RESTful API 接口，用于文件转换、预览和下载。所有 API 都返回 JSON 格式的响应。

## 基础信息

- 基础 URL: `http://localhost:5001/api`
- 响应格式: JSON
- 字符编码: UTF-8
- 请求方式: 所有API都支持GET和POST请求

## 认证

当前版本不需要认证，但建议在生产环境中使用 HTTPS 和适当的认证机制。

## 错误处理

所有 API 在发生错误时都会返回以下格式的响应：

```json
{
    "status": "failed",
    "message": "错误描述信息",
    "error": "详细错误信息"
}
```

常见错误码：
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误

## 接口列表

1. [文件转换](./convert.md)
   - 上传文件转换
   - URL 文件转换
   - 转换状态查询

2. [文件预览](./preview.md)
   - 预览PDF文件
   - 预览Excel文件
   - 处理中文件的预览

3. [文件下载](./download.md)
   - 文件ID下载
   - 文件路径下载
   - 处理中文件的下载

4. [系统状态](./status.md)
   - 获取系统状态
   - 获取缓存信息

## 请求限制

- 文件大小限制: 16MB
- 请求频率限制: 60 次/分钟
- 并发请求限制: 10 个/用户

## 响应时间

- 文件转换: 通常在 1-30 秒之间，取决于文件大小
- 文件预览: 通常在 1-5 秒之间
- 文件下载: 取决于文件大小和网络速度

## 示例代码

### Python

```python
import requests

# 上传文件转换
files = {'file': open('document.docx', 'rb')}
response = requests.post('http://localhost:5001/api/convert', files=files)
data = response.json()
print(data)
# 预览和下载URL直接包含在响应中
preview_url = data.get('preview_url')
download_url = data.get('download_url')

# 转换 URL 文件
params = {'url': 'https://example.com/document.docx'}
response = requests.get('http://localhost:5001/api/convert', params=params)
data = response.json()
print(data)
# 获取转换状态
task_id = data.get('task_id')
status_response = requests.get(f'http://localhost:5001/api/convert/status?task_id={task_id}')
print(status_response.json())

# 文件下载
file_id = data.get('file_id')
download_response = requests.get(f'http://localhost:5001/api/files/download?file_id={file_id}')
with open('downloaded_file.pdf', 'wb') as f:
    f.write(download_response.content)
```

### JavaScript

```javascript
// 上传文件转换
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:5001/api/convert', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log(data);
  // 预览和下载URL直接包含在响应中
  const previewUrl = data.preview_url;
  const downloadUrl = data.download_url;
  // 可以直接使用这些URL进行预览或下载
  window.open(previewUrl);
});

// 转换 URL 文件
fetch('http://localhost:5001/api/convert?url=https://example.com/document.docx')
  .then(response => response.json())
  .then(data => {
    console.log(data);
    // 获取转换状态
    const taskId = data.task_id;
    return fetch(`http://localhost:5001/api/convert/status?task_id=${taskId}`);
  })
  .then(response => response.json())
  .then(statusData => {
    console.log(statusData);
  });
```

## 更新日志

### v0.2.0 (2024-04-15)
- 修改API路由，使用查询参数而非URL路径参数
- `/api/convert` 接口直接返回预览和下载URL
- 统一使用 `/preview` 路由进行文件预览
- 所有API接口同时支持GET和POST请求
- 添加文件转换中的动态加载界面

### v0.1.0 (2024-04-08)
- 初始版本发布
- 支持基本文件转换功能
- 支持文件预览和下载
- 支持 URL 文件转换 