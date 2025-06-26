# 文件预览 API

## 文件预览

在线预览各种类型的文件，包括PDF、Excel等。

### 请求

```
GET /preview
POST /preview
```

### 参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| file_id | String | 否 | 文件ID |
| file | String | 否 | 文件名 |
| url | String | 否 | 文件URL |
| task_id | String | 否 | 任务ID (用于等待转换完成的文件) |
| convert_to_pdf | Boolean | 否 | 是否转换为PDF格式预览，默认为 true |

**注意:** 以上参数至少需要提供一个

### 请求示例

```bash
# 通过文件ID预览
curl -X GET "http://localhost:5001/preview?file_id=abc123"

# 通过文件名预览
curl -X GET "http://localhost:5001/preview?file=document.pdf"

# 通过URL预览
curl -X GET "http://localhost:5001/preview?url=https://example.com/document.docx"

# 通过任务ID预览(显示加载状态)
curl -X GET "http://localhost:5001/preview?task_id=a1b2c3d4e5f6"

# Excel文件直接预览(不转换为PDF)
curl -X GET "http://localhost:5001/preview?file_id=abc123&convert_to_pdf=false"
```

### 响应

根据不同的参数和文件类型，响应会有所不同：

1. **PDF文件预览**: 返回HTML页面，内嵌PDF查看器
2. **Excel文件直接预览**: 返回HTML页面，使用专业Excel预览组件
3. **任务ID预览**: 返回加载页面，自动检查转换状态，完成后跳转到预览页面
4. **URL文件预览**: 重定向到转换API，然后跳转到加载页面

错误响应：
```json
{
    "status": "failed",
    "message": "找不到文件",
    "error": "文件不存在或已被删除"
}
```

## 文件类型支持

| 文件类型 | 预览方式 | 说明 |
|---------|---------|------|
| PDF (.pdf) | 内嵌PDF查看器 | 直接预览，无需转换 |
| Excel (.xls, .xlsx) | Excel专用查看器 | 支持直接预览或转换为PDF |
| Word (.doc, .docx) | 转换为PDF后预览 | 先转换再预览 |
| PowerPoint (.ppt, .pptx) | 转换为PDF后预览 | 先转换再预览 |
| 文本文件 (.txt, .rtf) | 转换为PDF后预览 | 先转换再预览 |
| 图片文件 (.jpg, .png, .gif) | 直接预览 | 部分格式可能需要转换 |

## 等待页面

对于需要转换的文件，预览时会先显示等待页面，包含：

1. 加载动画
2. 进度指示器
3. 自动检查转换状态
4. 完成后自动跳转到预览页面

## 错误码

| 错误码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 404 | 文件不存在 |
| 410 | 文件已过期 |
| 415 | 不支持的文件格式 |
| 500 | 服务器内部错误 |

## 示例代码

### Python

```python
import requests
import webbrowser

# 通过文件ID预览
file_id = 'abc123'
preview_url = f'http://localhost:5001/preview?file_id={file_id}'
webbrowser.open(preview_url)

# 通过任务ID预览(包含加载状态)
task_id = 'a1b2c3d4e5f6'
loading_url = f'http://localhost:5001/preview?task_id={task_id}'
webbrowser.open(loading_url)

# Excel文件直接预览
excel_preview_url = f'http://localhost:5001/preview?file_id={file_id}&convert_to_pdf=false'
webbrowser.open(excel_preview_url)
```

### JavaScript

```javascript
// 通过文件ID预览
function previewFile(fileId) {
  const previewUrl = `http://localhost:5001/preview?file_id=${fileId}`;
  window.open(previewUrl, '_blank');
}

// 通过任务ID预览(包含加载动画)
function previewTask(taskId) {
  const loadingUrl = `http://localhost:5001/preview?task_id=${taskId}`;
  window.open(loadingUrl, '_blank');
}

// 在页面中嵌入预览
function embedPreview(fileId, elementId) {
  const previewUrl = `http://localhost:5001/preview?file_id=${fileId}`;
  const iframe = document.createElement('iframe');
  iframe.src = previewUrl;
  iframe.width = '100%';
  iframe.height = '600px';
  iframe.style.border = 'none';
  document.getElementById(elementId).appendChild(iframe);
}
```

## 浏览器兼容性

- Chrome: 完全支持
- Firefox: 完全支持
- Safari: 完全支持
- Edge: 完全支持
- IE: 不支持

## 安全建议

1. 在生产环境中使用HTTPS
2. 限制文件访问权限和域名
3. 定期清理过期文件
4. 为预览页面添加超时机制 