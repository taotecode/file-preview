# 用户指南

## 快速开始

### 1. 安装

```bash
pip install file-preview
```

### 2. 配置

创建配置文件 `config.yaml`：

```yaml
directories:
  cache: /path/to/cache
  download: /path/to/download
  convert: /path/to/convert
  log: /path/to/log

server:
  host: 0.0.0.0
  port: 5000

cache:
  retention_days: 7
  max_size: 1024

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

performance:
  max_workers: 4
  download_timeout: 30
  keep_original_name: true
  enable_multithreading: true
  worker_processes: 2

conversion:
  libreoffice_path: /usr/bin/libreoffice
  office_path: /Applications/Microsoft Office
  timeout: 300
  retry_times: 3
```

### 3. 启动服务

```bash
file-preview server --config /path/to/config.yaml
```

## 基本用法

### 1. 转换本地文件

```bash
file-preview convert /path/to/file.docx --output /path/to/output.pdf
```

### 2. 转换网络文件

```bash
file-preview convert-url https://example.com/file.docx --output /path/to/output.pdf
```

### 3. 清理缓存

```bash
file-preview cleanup --config /path/to/config.yaml
```

## Web 界面使用

### 1. 上传文件转换

1. 打开浏览器访问 `http://localhost:5000`
2. 点击"选择文件"按钮
3. 选择要转换的文件
4. 点击"转换"按钮
5. 等待转换完成
6. 点击"预览"或"下载"按钮

### 2. URL 文件转换

1. 打开浏览器访问 `http://localhost:5000`
2. 在 URL 输入框中输入文件地址
3. 点击"转换"按钮
4. 等待转换完成
5. 点击"预览"或"下载"按钮

## 支持的格式

- Microsoft Word (.doc, .docx)
- Microsoft Excel (.xls, .xlsx)
- 纯文本 (.txt)

## 常见问题

### 1. 文件转换失败

可能的原因：
- 文件格式不支持
- 文件损坏
- LibreOffice 未正确安装
- 内存不足

解决方法：
1. 检查文件格式是否支持
2. 重新下载或获取文件
3. 确保 LibreOffice 已正确安装
4. 增加系统内存或调整配置

### 2. 预览无法加载

可能的原因：
- PDF 文件生成失败
- 服务器未运行
- 文件权限问题

解决方法：
1. 检查转换日志
2. 重启服务器
3. 检查文件权限

### 3. 性能问题

可能的原因：
- 并发请求过多
- 缓存空间不足
- 系统资源不足

解决方法：
1. 增加工作线程数
2. 清理缓存
3. 优化系统配置

## 最佳实践

### 1. 文件处理

- 使用标准格式的文件
- 避免过大的文件
- 定期清理不需要的文件

### 2. 系统维护

- 定期检查日志
- 监控系统资源
- 及时更新软件

### 3. 安全建议

- 使用 HTTPS
- 限制文件大小
- 设置访问权限
- 定期备份数据

## 故障排除

### 1. 查看日志

```bash
tail -f /path/to/log/file_preview.log
```

### 2. 检查系统状态

```bash
file-preview status --config /path/to/config.yaml
```

### 3. 清理缓存

```bash
file-preview cleanup --config /path/to/config.yaml
```

## 联系支持

- 问题反馈：https://github.com/taotecode/file-preview/issues
- 文档：https://github.com/taotecode/file-preview#readme
- 邮件：taotecode@example.com