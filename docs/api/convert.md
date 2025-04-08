# 文件转换 API

## 上传文件转换

将本地文件上传并转换为 PDF 格式。

### 请求

```
POST /api/convert
```

### 参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| file | File | 是 | 要转换的文件 |

### 请求示例

```bash
curl -X POST -F "file=@document.docx" http://localhost:5000/api/convert
```

### 响应

成功响应：
```json
{
    "success": true,
    "pdf_url": "http://localhost:5000/api/preview/converted_file.pdf",
    "download_url": "http://localhost:5000/api/download/converted_file.pdf"
}
```

错误响应：
```json
{
    "error": "不支持的文件格式"
}
```

## URL 文件转换

将网络文件下载并转换为 PDF 格式。

### 请求

```
GET /api/convert/url
```

### 参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| url | String | 是 | 要转换的文件 URL |
| direct_preview | Boolean | 否 | 是否直接跳转到预览页面，默认为 false |

### 请求示例

```bash
curl -X GET "http://localhost:5000/api/convert/url?url=https://example.com/document.docx"
```

### 响应

成功响应：
```json
{
    "success": true,
    "pdf_url": "http://localhost:5000/api/preview/converted_file.pdf",
    "download_url": "http://localhost:5000/api/download/converted_file.pdf"
}
```

错误响应：
```json
{
    "error": "文件下载失败"
}
```

## 注意事项

1. 文件大小限制为 16MB
2. 支持的文件格式：
   - Microsoft Word (.doc, .docx)
   - Microsoft Excel (.xls, .xlsx)
   - 纯文本 (.txt)
3. 转换过程可能需要一些时间，取决于文件大小
4. 转换后的文件会保存在缓存中，可以通过预览和下载接口访问
5. 如果设置了 `direct_preview=true`，将直接跳转到预览页面

## 错误码

| 错误码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 404 | 文件不存在 |
| 413 | 文件大小超过限制 |
| 415 | 不支持的文件格式 |
| 500 | 服务器内部错误 |
| 502 | 文件下载失败 |
| 504 | 转换超时 |

## 示例代码

### Python

```python
import requests

# 上传文件转换
files = {'file': open('document.docx', 'rb')}
response = requests.post('http://localhost:5000/api/convert', files=files)
data = response.json()
if data['success']:
    print(f"预览地址: {data['pdf_url']}")
    print(f"下载地址: {data['download_url']}")
else:
    print(f"错误: {data['error']}")

# URL 文件转换
params = {
    'url': 'https://example.com/document.docx',
    'direct_preview': True
}
response = requests.get('http://localhost:5000/api/convert/url', params=params)
data = response.json()
if data['success']:
    print(f"预览地址: {data['pdf_url']}")
    print(f"下载地址: {data['download_url']}")
else:
    print(f"错误: {data['error']}")
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
.then(data => {
  if (data.success) {
    console.log(`预览地址: ${data.pdf_url}`);
    console.log(`下载地址: ${data.download_url}`);
  } else {
    console.error(`错误: ${data.error}`);
  }
});

// URL 文件转换
const params = new URLSearchParams({
  url: 'https://example.com/document.docx',
  direct_preview: true
});

fetch(`http://localhost:5000/api/convert/url?${params}`)
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log(`预览地址: ${data.pdf_url}`);
      console.log(`下载地址: ${data.download_url}`);
    } else {
      console.error(`错误: ${data.error}`);
    }
  });
``` 