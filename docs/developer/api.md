# API 文档

本文档详细介绍了 File Preview 项目的 API 接口。

## 基础信息

- 基础路径: `/api`
- 请求格式: `application/json`
- 响应格式: `application/json`
- 字符编码: `UTF-8`

## 认证方式

目前支持以下认证方式：

1. API Key 认证
   - 在请求头中添加 `X-API-Key`
   - 示例: `X-API-Key: your-api-key`

2. JWT 认证
   - 在请求头中添加 `Authorization: Bearer <token>`
   - 示例: `Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...`

## 错误码

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求参数是否符合要求 |
| 401 | 未授权 | 检查认证信息是否正确 |
| 403 | 禁止访问 | 检查权限设置 |
| 404 | 资源不存在 | 检查请求的资源是否存在 |
| 500 | 服务器内部错误 | 联系管理员 |

## 文件转换 API

### 1. 上传文件转换

将本地文件转换为 PDF。

**请求**

```
POST /api/convert
```

**请求头**

```
Content-Type: multipart/form-data
```

**请求参数**

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| file | File | 是 | 要转换的文件 |
| keep_original_name | Boolean | 否 | 是否保留原始文件名，默认为 false |

**响应**

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "file_id": "a1b2c3d4e5f6",
        "preview_url": "/preview/a1b2c3d4e5f6",
        "download_url": "/download/a1b2c3d4e5f6"
    }
}
```

### 2. URL 文件转换

将网络文件转换为 PDF。

**请求**

```
POST /api/convert/url
```

**请求头**

```
Content-Type: application/json
```

**请求参数**

```json
{
    "url": "https://example.com/document.docx",
    "keep_original_name": true
}
```

**响应**

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "file_id": "a1b2c3d4e5f6",
        "preview_url": "/preview/a1b2c3d4e5f6",
        "download_url": "/download/a1b2c3d4e5f6"
    }
}
```

## 文件预览 API

### 1. 预览文件

预览转换后的 PDF 文件。

**请求**

```
GET /preview/{file_id}
```

**请求参数**

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| file_id | String | 是 | 文件 ID |

**响应**

返回 HTML 页面，直接显示 PDF 文件。

### 2. 获取转换状态

获取文件转换的状态。

**请求**

```
GET /api/status/{file_id}
```

**请求参数**

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| file_id | String | 是 | 文件 ID |

**响应**

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "status": "completed",
        "progress": 100,
        "error": null
    }
}
```

状态说明：
- `pending`: 等待转换
- `processing`: 转换中
- `completed`: 转换完成
- `failed`: 转换失败

## 文件下载 API

### 1. 下载文件

下载转换后的 PDF 文件。

**请求**

```
GET /download/{file_id}
```

**请求参数**

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| file_id | String | 是 | 文件 ID |

**响应**

返回 PDF 文件流。

## 缓存管理 API

### 1. 清理缓存

清理过期的缓存文件。

**请求**

```
POST /api/cache/cleanup
```

**请求头**

```
Content-Type: application/json
```

**请求参数**

```json
{
    "retention_days": 7
}
```

**响应**

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "deleted_files": 10,
        "freed_space": "1.5GB"
    }
}
```

## 系统信息 API

### 1. 获取系统状态

获取系统运行状态信息。

**请求**

```
GET /api/status
```

**响应**

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "version": "1.0.0",
        "uptime": "2d 5h 30m",
        "memory_usage": "45%",
        "cpu_usage": "30%",
        "disk_usage": "60%",
        "active_conversions": 5,
        "total_conversions": 1000
    }
}
```

## WebSocket API

### 1. 转换状态推送

实时推送文件转换状态。

**连接**

```
WS /ws/status/{file_id}
```

**消息格式**

```json
{
    "status": "processing",
    "progress": 50,
    "error": null
}
```

## 限流策略

API 请求限制：

| API 路径 | 限制 | 时间窗口 |
|----------|------|----------|
| /api/convert | 100 次/分钟 | 1 分钟 |
| /api/convert/url | 50 次/分钟 | 1 分钟 |
| /api/cache/cleanup | 10 次/小时 | 1 小时 |
| /api/status | 1000 次/分钟 | 1 分钟 |

## 示例代码

### Python

```python
import requests

# 上传文件转换
def convert_file(file_path):
    url = "http://localhost:5000/api/convert"
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, files=files)
    return response.json()

# URL 文件转换
def convert_url(file_url):
    url = "http://localhost:5000/api/convert/url"
    data = {'url': file_url}
    response = requests.post(url, json=data)
    return response.json()

# 获取转换状态
def get_status(file_id):
    url = f"http://localhost:5000/api/status/{file_id}"
    response = requests.get(url)
    return response.json()
```

### JavaScript

```javascript
// 上传文件转换
async function convertFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('http://localhost:5000/api/convert', {
        method: 'POST',
        body: formData
    });
    return await response.json();
}

// URL 文件转换
async function convertUrl(fileUrl) {
    const response = await fetch('http://localhost:5000/api/convert/url', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: fileUrl })
    });
    return await response.json();
}

// WebSocket 状态监听
function listenStatus(fileId) {
    const ws = new WebSocket(`ws://localhost:5000/ws/status/${fileId}`);
    
    ws.onmessage = (event) => {
        const status = JSON.parse(event.data);
        console.log('转换状态:', status);
    };
}
```

## 注意事项

1. 文件大小限制
   - 单个文件最大 100MB
   - 支持的文件格式见配置文档

2. 并发限制
   - 单个 IP 最大并发数：10
   - 单个用户最大并发数：5

3. 缓存策略
   - 默认缓存时间：7 天
   - 最大缓存空间：1GB

4. 错误重试
   - 最大重试次数：3
   - 重试间隔：5 秒

## 更新日志

### v1.0.0 (2024-03-20)
- 初始版本发布
- 支持基本文件转换功能
- 支持文件预览和下载
- 支持缓存管理
- 提供完整的 API 文档 