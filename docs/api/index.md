# API 文档

## 概述

文件预览工具提供了一组 RESTful API 接口，用于文件转换、预览和下载。所有 API 都返回 JSON 格式的响应。

## 基础信息

- 基础 URL: `http://localhost:5000/api`
- 响应格式: JSON
- 字符编码: UTF-8

## 认证

当前版本不需要认证，但建议在生产环境中使用 HTTPS 和适当的认证机制。

## 错误处理

所有 API 在发生错误时都会返回以下格式的响应：

```json
{
    "error": "错误描述信息"
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

2. [文件预览](./preview.md)
   - 预览 PDF 文件

3. [文件下载](./download.md)
   - 下载 PDF 文件

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
response = requests.post('http://localhost:5000/api/convert', files=files)
print(response.json())

# 转换 URL 文件
params = {'url': 'https://example.com/document.docx'}
response = requests.get('http://localhost:5000/api/convert/url', params=params)
print(response.json())
```

### JavaScript

```javascript
// 上传文件转换
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:5000/api/convert', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));

// 转换 URL 文件
fetch('http://localhost:5000/api/convert/url?url=https://example.com/document.docx')
  .then(response => response.json())
  .then(data => console.log(data));
```

## 更新日志

### v0.1.0 (2024-04-08)
- 初始版本发布
- 支持基本文件转换功能
- 支持文件预览和下载
- 支持 URL 文件转换 