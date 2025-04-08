# 核心 API 文档

本文档详细说明了 File Preview 的核心 API 接口。所有 API 接口都遵循 RESTful 设计规范。

## 基础信息

- 基础 URL: `http://localhost:5000/api`
- 内容类型: `application/json`
- 字符编码: `UTF-8`

## 认证

目前 API 不需要认证，但建议在生产环境中添加认证机制。

## 错误处理

所有 API 错误都会返回 JSON 格式的错误信息：

```json
{
  "error": "错误描述",
  "code": "错误代码"
}
```

常见错误代码：

- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

## API 端点

### 1. 转换本地文件

```
POST /api/convert
```

将本地文件转换为 PDF 格式。

#### 请求参数

- `file`: 文件（multipart/form-data）
- `keep_original_name`: 是否保持原始文件名（可选，布尔值）

#### 响应

成功响应：
```json
{
  "status": "success",
  "filename": "converted.pdf",
  "preview_url": "/api/preview/converted.pdf",
  "download_url": "/api/download/converted.pdf"
}
```

错误响应：
```json
{
  "error": "不支持的文件格式",
  "code": "400"
}
```

#### 示例

```bash
curl -X POST -F "file=@document.docx" http://localhost:5000/api/convert
```

### 2. 转换网络文件

```
GET /api/convert/url
```

将网络文件转换为 PDF 格式。

#### 请求参数

- `url`: 文件 URL（查询参数）
- `keep_original_name`: 是否保持原始文件名（可选，布尔值）

#### 响应

成功响应：
```json
{
  "status": "success",
  "filename": "converted.pdf",
  "preview_url": "/api/preview/converted.pdf",
  "download_url": "/api/download/converted.pdf"
}
```

错误响应：
```json
{
  "error": "URL 无效",
  "code": "400"
}
```

#### 示例

```bash
curl "http://localhost:5000/api/convert/url?url=https://example.com/document.docx"
```

### 3. 预览文件

```
GET /api/preview/{filename}
```

预览转换后的 PDF 文件。

#### 请求参数

- `filename`: PDF 文件名（路径参数）

#### 响应

成功响应：
- 返回 PDF 文件的 HTML 预览页面

错误响应：
```json
{
  "error": "文件不存在",
  "code": "404"
}
```

#### 示例

```bash
curl http://localhost:5000/api/preview/converted.pdf
```

### 4. 下载文件

```
GET /api/download/{filename}
```

下载转换后的 PDF 文件。

#### 请求参数

- `filename`: PDF 文件名（路径参数）

#### 响应

成功响应：
- 返回 PDF 文件下载

错误响应：
```json
{
  "error": "文件不存在",
  "code": "404"
}
```

#### 示例

```bash
curl -o output.pdf http://localhost:5000/api/download/converted.pdf
```

### 5. 获取文件信息

```
GET /api/info/{filename}
```

获取文件的基本信息。

#### 请求参数

- `filename`: 文件名（路径参数）

#### 响应

成功响应：
```json
{
  "filename": "document.pdf",
  "size": 1024000,
  "created_at": "2023-01-01T00:00:00Z",
  "modified_at": "2023-01-01T00:00:00Z",
  "format": "pdf"
}
```

错误响应：
```json
{
  "error": "文件不存在",
  "code": "404"
}
```

#### 示例

```bash
curl http://localhost:5000/api/info/converted.pdf
```

### 6. 清理缓存

```
POST /api/cleanup
```

清理过期的缓存文件。

#### 请求参数

- `days`: 保留天数（可选，整数）

#### 响应

成功响应：
```json
{
  "status": "success",
  "deleted_files": 10,
  "freed_space": 10485760
}
```

错误响应：
```json
{
  "error": "清理失败",
  "code": "500"
}
```

#### 示例

```bash
curl -X POST "http://localhost:5000/api/cleanup?days=7"
```

## 状态码

- `200`: 请求成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

## 限流

API 默认没有限流，但建议在生产环境中添加限流机制。

## 安全建议

1. 在生产环境中启用 HTTPS
2. 添加 API 认证机制
3. 实现请求限流
4. 验证文件类型和大小
5. 定期清理缓存文件

## 客户端示例

### Python

```python
import requests

def convert_file(file_path):
    url = "http://localhost:5000/api/convert"
    files = {"file": open(file_path, "rb")}
    response = requests.post(url, files=files)
    return response.json()

def convert_url(file_url):
    url = "http://localhost:5000/api/convert/url"
    params = {"url": file_url}
    response = requests.get(url, params=params)
    return response.json()
```

### JavaScript

```javascript
async function convertFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('http://localhost:5000/api/convert', {
        method: 'POST',
        body: formData
    });
    return await response.json();
}

async function convertUrl(url) {
    const response = await fetch(`http://localhost:5000/api/convert/url?url=${encodeURIComponent(url)}`);
    return await response.json();
}
```

## 最佳实践

1. 文件上传
   - 限制文件大小
   - 验证文件类型
   - 使用分块上传大文件

2. 错误处理
   - 实现重试机制
   - 记录错误日志
   - 提供友好的错误信息

3. 性能优化
   - 使用缓存
   - 异步处理大文件
   - 压缩响应数据

4. 安全措施
   - 验证文件内容
   - 限制并发请求
   - 定期清理临时文件 