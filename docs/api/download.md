# 文件下载 API

## 下载 PDF 文件

下载转换后的 PDF 文件。

### 请求

```
GET /api/download/{filename}
```

### 参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| filename | String | 是 | PDF 文件名 |

### 请求示例

```bash
curl -X GET http://localhost:5000/api/download/converted_file.pdf -o output.pdf
```

### 响应

成功响应：
- 返回 PDF 文件内容，Content-Type 为 `application/pdf`
- Content-Disposition 头包含文件名

错误响应：
```json
{
    "error": "文件不存在"
}
```

## 注意事项

1. 文件名必须是有效的 PDF 文件名
2. 文件必须存在于缓存中
3. 下载的文件名可以通过 Content-Disposition 头获取
4. 支持断点续传
5. 支持大文件下载

## 错误码

| 错误码 | 描述 |
|--------|------|
| 404 | 文件不存在 |
| 410 | 文件已过期 |
| 416 | 请求范围不满足 |
| 500 | 服务器内部错误 |

## 示例代码

### Python

```python
import requests

# 下载 PDF 文件
filename = 'converted_file.pdf'
response = requests.get(f'http://localhost:5000/api/download/{filename}', stream=True)

if response.status_code == 200:
    # 获取文件名
    content_disposition = response.headers.get('content-disposition')
    if content_disposition:
        filename = content_disposition.split('filename=')[1].strip('"')
    
    # 下载文件
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"文件已下载: {filename}")
else:
    print(f"错误: {response.json()['error']}")

# 断点续传
def download_with_resume(url, filename):
    headers = {}
    if os.path.exists(filename):
        # 获取已下载文件大小
        size = os.path.getsize(filename)
        headers['Range'] = f'bytes={size}-'
    
    response = requests.get(url, headers=headers, stream=True)
    
    if response.status_code == 206:  # 部分内容
        mode = 'ab'
    else:
        mode = 'wb'
    
    with open(filename, mode) as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
```

### JavaScript

```javascript
// 下载 PDF 文件
const filename = 'converted_file.pdf';

fetch(`http://localhost:5000/api/download/${filename}`)
  .then(response => {
    if (!response.ok) {
      return response.json().then(data => {
        throw new Error(data.error);
      });
    }
    
    // 获取文件名
    const contentDisposition = response.headers.get('content-disposition');
    let downloadFilename = filename;
    if (contentDisposition) {
      const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
      if (matches != null && matches[1]) {
        downloadFilename = matches[1].replace(/['"]/g, '');
      }
    }
    
    return response.blob().then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = downloadFilename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    });
  })
  .catch(error => {
    console.error(`错误: ${error.message}`);
  });

// 断点续传
async function downloadWithResume(url, filename) {
  let response;
  const fileSize = await getFileSize(filename);
  
  if (fileSize > 0) {
    response = await fetch(url, {
      headers: {
        'Range': `bytes=${fileSize}-`
      }
    });
  } else {
    response = await fetch(url);
  }
  
  if (!response.ok) {
    throw new Error(`下载失败: ${response.status}`);
  }
  
  const reader = response.body.getReader();
  const writer = new FileWriter(filename);
  
  while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    await writer.write(value);
  }
  
  await writer.close();
}
```

## 性能优化

1. 使用流式下载处理大文件
2. 支持断点续传
3. 使用压缩传输
4. 支持并行下载
5. 缓存控制

## 安全建议

1. 在生产环境中使用 HTTPS
2. 限制下载频率
3. 验证文件权限
4. 监控异常下载
5. 定期清理过期文件 