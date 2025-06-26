# 使用指南

## 文件映射功能

File Preview 提供了文件映射功能，可以避免重复转换相同的文件。系统会：

1. 计算文件的 MD5 值作为唯一标识
2. 将文件映射关系存储在 `cache/file_mappings.json` 中
3. 在转换前检查映射关系
4. 如果文件已转换过，直接使用已转换的文件

### 映射文件格式

```json
{
  "md5_hash1": "/path/to/converted/file1.pdf",
  "md5_hash2": "/path/to/converted/file2.pdf"
}
```

### 映射规则

1. 本地文件：
   - 使用文件内容的 MD5 值作为标识
   - 映射到转换后的 PDF 文件路径

2. 网络文件：
   - 使用 URL 的 MD5 值作为标识
   - 使用文件内容的 MD5 值作为标识
   - 同时映射到转换后的 PDF 文件路径

## 命令行工具

### 1. 启动服务

#### 直接执行（无需编译）：
```bash
python -m file_preview.cli.main server
```

#### 使用安装后的命令：
```bash
file-preview server --config /path/to/config.yaml
```

### 2. 转换本地文件

#### 直接执行（无需编译）：
```bash
python -m file_preview.cli.main convert /path/to/file.docx --output /path/to/output.pdf
```

#### 使用安装后的命令：
```bash
file-preview convert /path/to/file.docx --output /path/to/output.pdf
```

### 3. 转换网络文件

#### 直接执行（无需编译）：
```bash
python -m file_preview.cli.main convert-url https://example.com/file.docx --output /path/to/output.pdf
```

#### 使用安装后的命令：
```bash
file-preview convert-url https://example.com/file.docx --output /path/to/output.pdf
```

### 4. 清理缓存

#### 直接执行：
```bash
python -m file_preview.cli.main cleanup
```

#### 使用安装后的命令：
```bash
file-preview cleanup --config /path/to/config.yaml
```

## API 接口

### 1. 上传文件转换

```bash
curl -X POST -F "file=@/path/to/file.docx" http://localhost:5000/api/convert
```

响应示例：
```json
{
    "success": true,
    "pdf_url": "http://localhost:5000/api/preview/converted_file.pdf",
    "download_url": "http://localhost:5000/api/download/converted_file.pdf"
}
```

### 2. 转换网络文件

```bash
curl -X GET "http://localhost:5000/api/convert?url=https://example.com/file.docx"
```

响应示例：
```json
{
    "success": true,
    "pdf_url": "http://localhost:5000/api/preview/converted_file.pdf",
    "download_url": "http://localhost:5000/api/download/converted_file.pdf"
}
```

### 3. 直接预览网络文件

```bash
curl -X GET "http://localhost:5000/api/preview/url?url=https://example.com/file.docx"
```

这个接口会：
1. 检查文件是否已转换
2. 如果已转换，直接返回 PDF 文件
3. 如果未转换，显示加载动画并开始转换
4. 转换完成后自动跳转到预览页面

## 支持的格式

- Microsoft Word (.doc, .docx)
- Microsoft Excel (.xls, .xlsx)
- 纯文本 (.txt)

## 配置选项

### 目录配置

- `cache`: 缓存文件目录
- `download`: 下载文件临时目录
- `convert`: 转换文件临时目录
- `log`: 日志目录

### 服务器配置

- `host`: 服务器主机地址
- `port`: 服务器端口

### 缓存配置

- `retention_days`: 缓存保留天数
- `max_size`: 最大缓存大小（MB）

### 日志配置

- `level`: 日志级别
- `format`: 日志格式

### 性能配置

- `max_workers`: 最大工作线程数
- `download_timeout`: 下载超时时间（秒）
- `keep_original_name`: 是否保留原始文件名
- `enable_multithreading`: 是否启用多线程模式
- `worker_processes`: 工作进程数

### 转换配置

- `libreoffice_path`: LibreOffice 可执行文件路径
- `office_path`: Microsoft Office 安装路径
- `timeout`: 转换超时时间（秒）
- `retry_times`: 转换失败重试次数

## 常见问题

### 1. 文件转换失败

- 检查文件格式是否支持
- 确保 LibreOffice 已正确安装
- 查看日志文件中的错误信息

### 2. 预览无法加载

- 检查 PDF 文件是否成功生成
- 确认服务器是否正常运行
- 验证文件权限是否正确

### 3. 性能问题

- 增加 `max_workers` 和 `worker_processes`
- 调整缓存大小和保留时间
- 优化服务器配置

## 最佳实践

1. 使用 HTTPS 保护数据传输
2. 定期清理缓存文件
3. 监控服务器性能
4. 备份重要配置文件
5. 及时更新依赖包 