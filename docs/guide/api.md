# 文件预览系统API参考文档

## 1. API概述

文件预览系统提供了一组REST API，用于文件上传、下载、转换和预览。所有API端点均使用JSON格式进行数据交换，并返回标准的HTTP状态码。

### 1.1 基础URL

所有API请求的基础URL为：

```
http://<server_host>:<server_port>/api
```

其中`<server_host>`和`<server_port>`是服务器的主机名和端口号，默认为`localhost:5001`。

### 1.2 认证方式

目前API不要求认证。在生产环境中，建议实施适当的认证机制。

### 1.3 响应格式

所有API响应均使用JSON格式，基本结构如下：

```json
{
  "status": "success",  // 或 "failed"
  "data": {},           // 操作成功时返回的数据
  "error": ""           // 操作失败时返回的错误信息
}
```

## 2. 服务器状态API

### 2.1 获取服务器状态

获取服务器当前运行状态和基本信息。

**请求：**

```
GET /stats
```

**响应：**

```json
{
  "status": "success",
  "data": {
    "server_status": "running",
    "version": "1.0.0",
    "uptime": "10:23:45",
    "tasks_in_queue": 0,
    "files_processed": 156
  }
}
```

## 3. 文件操作API

### 3.1 上传文件

上传本地文件到服务器。

**请求：**

```
POST /upload
Content-Type: multipart/form-data
```

**参数：**

| 参数名 | 类型 | 必填 | 描述 |
| ----- | ---- | ---- | ---- |
| file | File | 是 | 要上传的文件 |

**响应：**

```json
{
  "status": "success",
  "data": {
    "file_id": "f12345678",
    "file_name": "example.doc",
    "file_size": 102400,
    "upload_time": "2023-08-15T10:30:45Z",
    "download_url": "/api/download/f12345678",
    "preview_url": "/view/f12345678"
  }
}
```

### 3.2 从URL获取文件

从指定URL获取文件并保存到服务器。

**请求：**

```
POST /url
Content-Type: application/json
```

**请求体：**

```json
{
  "url": "https://example.com/path/to/document.pdf"
}
```

**响应：**

```json
{
  "status": "success",
  "data": {
    "file_id": "f12345678",
    "file_name": "document.pdf",
    "file_size": 204800,
    "task_id": "t87654321",
    "status_url": "/api/status/t87654321",
    "download_url": "/api/download/f12345678",
    "preview_url": "/view/f12345678"
  }
}
```

### 3.3 批量URL处理

批量从多个URL获取文件。

**请求：**

```
POST /batch_url
Content-Type: application/json
```

**请求体：**

```json
{
  "urls": [
    "https://example.com/document1.pdf",
    "https://example.com/document2.docx",
    "https://example.com/document3.xlsx"
  ]
}
```

**响应：**

```json
{
  "status": "success",
  "data": {
    "batch_id": "b12345678",
    "total_files": 3,
    "status_url": "/api/batch_status/b12345678",
    "tasks": [
      {
        "url": "https://example.com/document1.pdf",
        "task_id": "t11111111",
        "status": "processing"
      },
      {
        "url": "https://example.com/document2.docx",
        "task_id": "t22222222",
        "status": "processing"
      },
      {
        "url": "https://example.com/document3.xlsx",
        "task_id": "t33333333",
        "status": "processing"
      }
    ]
  }
}
```

### 3.4 下载文件

下载指定ID的文件。

**请求：**

```
GET /download/{file_id}
```

**参数：**

| 参数名 | 类型 | 必填 | 描述 |
| ----- | ---- | ---- | ---- |
| file_id | string | 是 | 文件ID |

**响应：**

文件内容将直接返回，Content-Type将设置为相应的MIME类型。

### 3.5 获取文件信息

获取指定ID的文件详细信息。

**请求：**

```
GET /info/{file_id}
```

**参数：**

| 参数名 | 类型 | 必填 | 描述 |
| ----- | ---- | ---- | ---- |
| file_id | string | 是 | 文件ID |

**响应：**

```json
{
  "status": "success",
  "data": {
    "file_id": "f12345678",
    "file_name": "example.doc",
    "file_type": "application/msword",
    "file_size": 102400,
    "upload_time": "2023-08-15T10:30:45Z",
    "last_access": "2023-08-15T11:45:30Z",
    "download_count": 5,
    "preview_count": 12,
    "download_url": "/api/download/f12345678",
    "preview_url": "/view/f12345678",
    "converted": true,
    "converted_files": [
      {
        "format": "pdf",
        "size": 98560,
        "preview_url": "/view/f12345678?format=pdf"
      }
    ]
  }
}
```

### 3.6 删除文件

删除指定ID的文件。

**请求：**

```
DELETE /file/{file_id}
```

**参数：**

| 参数名 | 类型 | 必填 | 描述 |
| ----- | ---- | ---- | ---- |
| file_id | string | 是 | 文件ID |

**响应：**

```json
{
  "status": "success",
  "data": {
    "message": "文件已成功删除"
  }
}
```

## 4. 文件转换API

### 4.1 转换文件

将指定ID的文件转换为其他格式。

**请求：**

```
POST /convert/{file_id}
Content-Type: application/json
```

**参数：**

| 参数名 | 类型 | 必填 | 描述 |
| ----- | ---- | ---- | ---- |
| file_id | string | 是 | 文件ID |

**请求体：**

```json
{
  "target_format": "pdf",  // 目标格式，支持 "pdf", "html", "png" 等
  "options": {             // 转换选项，可选
    "resolution": 300,     // 图像分辨率，针对图片和PDF
    "quality": "high",     // 质量设置
    "page_range": "1-5"    // 页面范围
  }
}
```

**响应：**

```json
{
  "status": "success",
  "data": {
    "task_id": "t87654321",
    "file_id": "f12345678",
    "target_format": "pdf",
    "status": "processing",
    "status_url": "/api/status/t87654321"
  }
}
```

### 4.2 获取转换任务状态

获取文件转换任务的状态。

**请求：**

```
GET /status/{task_id}
```

**参数：**

| 参数名 | 类型 | 必填 | 描述 |
| ----- | ---- | ---- | ---- |
| task_id | string | 是 | 任务ID |

**响应：**

```json
{
  "status": "success",
  "data": {
    "task_id": "t87654321",
    "file_id": "f12345678",
    "target_format": "pdf",
    "status": "completed",  // 可能的值: "pending", "processing", "completed", "failed"
    "progress": 100,         // 进度百分比
    "message": "转换完成",
    "result": {
      "converted_file_id": "f87654321",
      "download_url": "/api/download/f87654321",
      "preview_url": "/view/f87654321"
    }
  }
}
```

### 4.3 批量转换状态查询

获取批量转换任务的状态。

**请求：**

```
GET /batch_status/{batch_id}
```

**参数：**

| 参数名 | 类型 | 必填 | 描述 |
| ----- | ---- | ---- | ---- |
| batch_id | string | 是 | 批次ID |

**响应：**

```json
{
  "status": "success",
  "data": {
    "batch_id": "b12345678",
    "total_files": 3,
    "completed": 2,
    "processing": 1,
    "failed": 0,
    "tasks": [
      {
        "task_id": "t11111111",
        "file_id": "f11111111",
        "status": "completed",
        "preview_url": "/view/f11111111"
      },
      {
        "task_id": "t22222222",
        "file_id": "f22222222",
        "status": "completed",
        "preview_url": "/view/f22222222"
      },
      {
        "task_id": "t33333333",
        "file_id": null,
        "status": "processing"
      }
    ]
  }
}
```

## 5. 文件预览API

### 5.1 预览文件

预览指定ID的文件。

**请求：**

```
GET /view/{file_id}
```

**参数：**

| 参数名 | 类型 | 必填 | 描述 |
| ----- | ---- | ---- | ---- |
| file_id | string | 是 | 文件ID |
| format | string | 否 | 预览格式，如 "pdf", "html" 等 |
| page | integer | 否 | 指定页码，默认为1 |

**响应：**

返回HTML页面或相应格式的文件内容。

### 5.2 获取缩略图

获取文件的缩略图。

**请求：**

```
GET /thumbnail/{file_id}
```

**参数：**

| 参数名 | 类型 | 必填 | 描述 |
| ----- | ---- | ---- | ---- |
| file_id | string | 是 | 文件ID |
| width | integer | 否 | 缩略图宽度，默认为200 |
| height | integer | 否 | 缩略图高度，默认为200 |
| page | integer | 否 | 多页文件的页码，默认为1 |

**响应：**

返回图片内容，Content-Type为image/png或image/jpeg。

## 6. 系统配置API

### 6.1 获取系统配置

获取系统配置信息。

**请求：**

```
GET /config
```

**响应：**

```json
{
  "status": "success",
  "data": {
    "allowed_file_types": [".doc", ".docx", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx", ".jpg", ".png"],
    "max_file_size": 52428800,  // 50MB
    "conversion_formats": {
      "document": ["pdf", "html"],
      "spreadsheet": ["pdf", "html"],
      "presentation": ["pdf", "html"],
      "image": ["jpg", "png", "webp"]
    },
    "thumbnail_sizes": {
      "small": [100, 100],
      "medium": [200, 200],
      "large": [400, 400]
    }
  }
}
```

### 6.2 更新系统配置

更新系统配置（需管理员权限）。

**请求：**

```
POST /config
Content-Type: application/json
```

**请求体：**

```json
{
  "max_file_size": 104857600,  // 100MB
  "conversion_timeout": 120,
  "cache_expiration": 86400    // 缓存过期时间（秒）
}
```

**响应：**

```json
{
  "status": "success",
  "data": {
    "message": "配置已更新",
    "updated_keys": ["max_file_size", "conversion_timeout", "cache_expiration"]
  }
}
```

## 7. 错误码参考

API可能返回以下错误码和错误消息：

| HTTP状态码 | 错误代码 | 描述 |
| --------- | ------- | ---- |
| 400 | INVALID_REQUEST | 请求格式无效 |
| 400 | INVALID_FILE | 文件格式无效或不支持 |
| 400 | FILE_TOO_LARGE | 文件大小超过限制 |
| 404 | FILE_NOT_FOUND | 文件未找到 |
| 404 | TASK_NOT_FOUND | 任务未找到 |
| 409 | FILE_EXISTS | 文件已存在 |
| 500 | CONVERSION_ERROR | 文件转换错误 |
| 500 | INTERNAL_ERROR | 内部服务器错误 |
| 503 | SERVICE_UNAVAILABLE | 服务暂时不可用 |

## 8. 示例代码

### 8.1 Python示例

使用Python请求文件预览系统API的示例：

```python
import requests
import json

# 服务器基础URL
BASE_URL = "http://localhost:5001/api"

# 上传文件
def upload_file(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    return response.json()

# 从URL获取文件
def download_from_url(url):
    data = {"url": url}
    response = requests.post(f"{BASE_URL}/url", json=data)
    return response.json()

# 检查任务状态
def check_task_status(task_id):
    response = requests.get(f"{BASE_URL}/status/{task_id}")
    return response.json()

# 示例使用
if __name__ == "__main__":
    # 上传文件
    result = upload_file("example.docx")
    if result["status"] == "success":
        file_id = result["data"]["file_id"]
        print(f"文件上传成功，ID: {file_id}")
        
        # 转换文件为PDF
        convert_data = {"target_format": "pdf"}
        convert_result = requests.post(f"{BASE_URL}/convert/{file_id}", json=convert_data).json()
        
        if convert_result["status"] == "success":
            task_id = convert_result["data"]["task_id"]
            print(f"转换任务已创建，ID: {task_id}")
            
            # 检查转换状态
            import time
            while True:
                status_result = check_task_status(task_id)
                status = status_result["data"]["status"]
                print(f"转换状态: {status}, 进度: {status_result['data'].get('progress', 0)}%")
                
                if status in ["completed", "failed"]:
                    break
                    
                time.sleep(2)
                
            if status == "completed":
                preview_url = status_result["data"]["result"]["preview_url"]
                print(f"转换完成，预览URL: {preview_url}")
    else:
        print(f"上传失败: {result.get('error', '')}")
```

### 8.2 JavaScript示例

使用JavaScript (Node.js或浏览器)请求文件预览系统API的示例：

```javascript
// 浏览器环境示例

// 服务器基础URL
const BASE_URL = "http://localhost:5001/api";

// 上传文件
async function uploadFile(fileInput) {
  const formData = new FormData();
  const file = fileInput.files[0];
  formData.append('file', file);
  
  try {
    const response = await fetch(`${BASE_URL}/upload`, {
      method: 'POST',
      body: formData
    });
    
    return await response.json();
  } catch (error) {
    console.error('上传文件出错:', error);
    return { status: 'failed', error: error.message };
  }
}

// 从URL获取文件
async function downloadFromUrl(url) {
  try {
    const response = await fetch(`${BASE_URL}/url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url })
    });
    
    return await response.json();
  } catch (error) {
    console.error('从URL获取文件出错:', error);
    return { status: 'failed', error: error.message };
  }
}

// 检查任务状态
async function checkTaskStatus(taskId) {
  try {
    const response = await fetch(`${BASE_URL}/status/${taskId}`);
    return await response.json();
  } catch (error) {
    console.error('检查任务状态出错:', error);
    return { status: 'failed', error: error.message };
  }
}

// 使用示例
document.getElementById('uploadForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const fileInput = document.getElementById('fileInput');
  const resultDiv = document.getElementById('result');
  
  resultDiv.innerHTML = '正在上传...';
  
  const uploadResult = await uploadFile(fileInput);
  
  if (uploadResult.status === 'success') {
    const fileId = uploadResult.data.file_id;
    resultDiv.innerHTML = `文件上传成功，ID: ${fileId}<br>`;
    
    // 转换文件为PDF
    const convertData = { target_format: 'pdf' };
    
    try {
      const convertResponse = await fetch(`${BASE_URL}/convert/${fileId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(convertData)
      });
      
      const convertResult = await convertResponse.json();
      
      if (convertResult.status === 'success') {
        const taskId = convertResult.data.task_id;
        resultDiv.innerHTML += `转换任务已创建，ID: ${taskId}<br>`;
        
        // 轮询检查转换状态
        const statusCheck = setInterval(async () => {
          const statusResult = await checkTaskStatus(taskId);
          const status = statusResult.data.status;
          const progress = statusResult.data.progress || 0;
          
          resultDiv.innerHTML += `转换状态: ${status}, 进度: ${progress}%<br>`;
          
          if (status === 'completed' || status === 'failed') {
            clearInterval(statusCheck);
            
            if (status === 'completed') {
              const previewUrl = statusResult.data.result.preview_url;
              resultDiv.innerHTML += `<a href="${previewUrl}" target="_blank">点击预览文件</a>`;
            }
          }
        }, 2000);
      }
    } catch (error) {
      resultDiv.innerHTML += `转换请求出错: ${error.message}`;
    }
  } else {
    resultDiv.innerHTML = `上传失败: ${uploadResult.error || '未知错误'}`;
  }
});
```

## 9. 限制与注意事项

1. **文件大小限制**: 默认最大上传文件大小为50MB。
2. **文件类型限制**: 系统支持常见的文档、表格、演示文稿和图像文件格式。
3. **转换时间**: 大文件转换可能需要较长时间，请使用任务状态API监控进度。
4. **API速率限制**: 未认证用户每分钟最多可发送60个请求。
5. **缓存策略**: 已转换的文件将缓存24小时，过期后需重新转换。
6. **URL限制**: 从URL获取文件时，URL必须可公开访问且文件大小不超过系统限制。

## 10. 联系与支持

如有API使用问题或建议，请联系：

- **邮箱**: support@example.com
- **问题追踪**: https://github.com/yourusername/file_previews/issues
- **文档网站**: https://docs.example.com/file_previews 