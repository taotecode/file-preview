# 文件转换 API

## 上传文件转换

将本地文件上传并转换为 PDF 格式。

### 请求

```
POST /api/convert
GET /api/convert
```

### 参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| file | File | 是(POST) | 要转换的文件(使用POST请求) |
| url | String | 是(GET) | 要转换的文件URL(使用GET请求) |
| file_id | String | 否 | 已上传文件的ID |
| convert_to_pdf | Boolean | 否 | 是否转换为PDF格式，默认为 true |

### 请求示例

```bash
# 上传文件转换
curl -X POST -F "file=@document.docx" http://localhost:5001/api/convert

# URL文件转换
curl -X GET "http://localhost:5001/api/convert?url=https://example.com/document.docx"

# 使用文件ID转换
curl -X GET "http://localhost:5001/api/convert?file_id=abc123&convert_to_pdf=true"
```

### 响应

成功响应：
```json
{
    "status": "success",
    "message": "文件转换任务已创建",
    "task_id": "a1b2c3d4e5f6",
    "file_id": "xyz789",
    "preview_url": "/preview?task_id=a1b2c3d4e5f6",
    "download_url": "/api/files/download?file_id=xyz789"
}
```

错误响应：
```json
{
    "status": "failed",
    "message": "不支持的文件类型",
    "error": "文件格式不被支持"
}
```

## 转换状态查询

查询文件转换任务的状态。

### 请求

```
GET /api/convert/status
POST /api/convert/status
```

### 参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| task_id | String | 是 | 任务ID |

### 请求示例

```bash
curl -X GET "http://localhost:5001/api/convert/status?task_id=a1b2c3d4e5f6"
```

### 响应

处理中响应：
```json
{
    "status": "processing",
    "message": "任务正在处理中",
    "progress": 50
}
```

成功响应：
```json
{
    "status": "success",
    "message": "处理完成",
    "filename": "document.pdf",
    "file_id": "xyz789",
    "download_url": "/api/files/download?file_id=xyz789",
    "preview_url": "/preview?file_id=xyz789"
}
```

失败响应：
```json
{
    "status": "failed",
    "message": "处理失败",
    "error": "文件格式不支持"
}
```

## 注意事项

1. 文件大小限制为 16MB
2. 支持的文件格式：
   - Microsoft Word (.doc, .docx)
   - Microsoft Excel (.xls, .xlsx)
   - Microsoft PowerPoint (.ppt, .pptx)
   - PDF (.pdf)
   - 纯文本 (.txt)
   - 图片文件 (.jpg, .jpeg, .png, .gif, .bmp)
3. 转换过程可能需要一些时间，可通过状态查询接口获取进度
4. 转换成功后，可直接使用返回的预览URL查看文件
5. 对于需要等待处理的任务，预览URL会自动显示加载进度并在完成后跳转到预览页面

## 错误码

| 错误码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 404 | 文件或任务不存在 |
| 413 | 文件大小超过限制 |
| 415 | 不支持的文件格式 |
| 500 | 服务器内部错误 |
| 502 | 文件下载失败 |
| 504 | 转换超时 |

## 示例代码

### Python

```python
import requests
import time

# 上传文件转换
files = {'file': open('document.docx', 'rb')}
response = requests.post('http://localhost:5001/api/convert', files=files)
data = response.json()
print(data)

# 任务ID和预览URL
task_id = data['task_id']
preview_url = data['preview_url']
download_url = data['download_url']

# 查询转换状态
status_response = requests.get(f'http://localhost:5001/api/convert/status?task_id={task_id}')
status_data = status_response.json()

# 等待转换完成
while status_data['status'] == 'processing':
    print(f"处理进度: {status_data.get('progress', 0)}%")
    time.sleep(1)
    status_response = requests.get(f'http://localhost:5001/api/convert/status?task_id={task_id}')
    status_data = status_response.json()

if status_data['status'] == 'success':
    print(f"转换完成: {status_data['preview_url']}")
else:
    print(f"转换失败: {status_data.get('error', '未知错误')}")

# URL文件转换
url_params = {'url': 'https://example.com/document.docx'}
response = requests.get('http://localhost:5001/api/convert', params=url_params)
data = response.json()
print(data)
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
  const taskId = data.task_id;
  const previewUrl = data.preview_url;
  
  // 可以直接重定向到预览页面，它会显示加载动画并自动刷新
  window.location.href = previewUrl;
  
  // 或者可以手动检查状态
  checkStatus(taskId);
});

// 检查转换状态
function checkStatus(taskId) {
  fetch(`http://localhost:5001/api/convert/status?task_id=${taskId}`)
    .then(response => response.json())
    .then(data => {
      if (data.status === 'processing') {
        console.log(`处理进度: ${data.progress || 0}%`);
        // 1秒后再次检查
        setTimeout(() => checkStatus(taskId), 1000);
      } else if (data.status === 'success') {
        console.log('转换完成!');
        console.log(`预览地址: ${data.preview_url}`);
        console.log(`下载地址: ${data.download_url}`);
      } else {
        console.error(`转换失败: ${data.error}`);
      }
    });
}

// URL文件转换
fetch('http://localhost:5001/api/convert?url=https://example.com/document.docx')
  .then(response => response.json())
  .then(data => {
    console.log(data);
    // 可以直接使用预览URL或下载URL
    console.log(`预览地址: ${data.preview_url}`);
    console.log(`下载地址: ${data.download_url}`);
  });
``` 