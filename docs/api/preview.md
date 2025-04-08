# 文件预览 API

## 预览 PDF 文件

在线预览转换后的 PDF 文件。

### 请求

```
GET /api/preview/{filename}
```

### 参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| filename | String | 是 | PDF 文件名 |

### 请求示例

```bash
curl -X GET http://localhost:5000/api/preview/converted_file.pdf
```

### 响应

成功响应：
- 返回 PDF 文件内容，Content-Type 为 `application/pdf`
- 浏览器会自动打开 PDF 预览

错误响应：
```json
{
    "error": "文件不存在"
}
```

## 注意事项

1. 文件名必须是有效的 PDF 文件名
2. 文件必须存在于缓存中
3. 预览页面支持基本的 PDF 查看功能：
   - 缩放
   - 翻页
   - 搜索
   - 打印

## 错误码

| 错误码 | 描述 |
|--------|------|
| 404 | 文件不存在 |
| 410 | 文件已过期 |
| 500 | 服务器内部错误 |

## 示例代码

### Python

```python
import requests
import webbrowser

# 预览 PDF 文件
filename = 'converted_file.pdf'
response = requests.get(f'http://localhost:5000/api/preview/{filename}')

if response.status_code == 200:
    # 保存文件并打开
    with open(filename, 'wb') as f:
        f.write(response.content)
    webbrowser.open(filename)
else:
    print(f"错误: {response.json()['error']}")
```

### JavaScript

```javascript
// 预览 PDF 文件
const filename = 'converted_file.pdf';

fetch(`http://localhost:5000/api/preview/${filename}`)
  .then(response => {
    if (response.ok) {
      return response.blob();
    }
    return response.json().then(data => {
      throw new Error(data.error);
    });
  })
  .then(blob => {
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
  })
  .catch(error => {
    console.error(`错误: ${error.message}`);
  });
```

## 浏览器兼容性

- Chrome: 支持
- Firefox: 支持
- Safari: 支持
- Edge: 支持
- IE: 不支持

## 安全建议

1. 在生产环境中使用 HTTPS
2. 限制文件访问权限
3. 定期清理过期文件
4. 监控异常访问 