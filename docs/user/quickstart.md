# 快速开始指南

本文档将帮助您快速上手使用 File Preview。我们将介绍如何使用二进制版本、Docker 版本和源码版本进行文件预览。

## 二进制版本使用

### 启动服务器

```bash
# 启动服务器
file-preview server

# 指定端口启动
file-preview server --port 8080

# 指定主机启动
file-preview server --host 0.0.0.0
```

### 转换本地文件

```bash
# 转换本地文件
file-preview convert /path/to/file.docx

# 指定输出路径
file-preview convert /path/to/file.docx --output /path/to/output.pdf

# 保持原始文件名
file-preview convert /path/to/file.docx --keep-original-name
```

### 转换网络文件

```bash
# 转换网络文件
file-preview convert-url https://example.com/file.docx

# 指定输出路径
file-preview convert-url https://example.com/file.docx --output /path/to/output.pdf
```

### 清理缓存

```bash
# 清理所有缓存
file-preview cleanup

# 清理指定天数前的缓存
file-preview cleanup --days 7
```

## Docker 版本使用

### 启动服务

```bash
# 使用默认配置启动
docker run -d \
  -p 5000:5000 \
  -v /path/to/config:/app/config \
  -v /path/to/cache:/app/cache \
  -v /path/to/download:/app/download \
  -v /path/to/log:/app/log \
  -v /path/to/convert:/app/convert \
  taotecode/file-preview:latest

# 使用 docker-compose 启动
docker-compose up -d
```

### 使用 API

1. 转换本地文件：
```bash
curl -X POST -F "file=@/path/to/file.docx" http://localhost:5000/api/convert
```

2. 转换网络文件：
```bash
curl "http://localhost:5000/api/convert/url?url=https://example.com/file.docx"
```

3. 预览文件：
```bash
# 在浏览器中打开
http://localhost:5000/api/preview/filename.pdf
```

4. 下载文件：
```bash
curl -o output.pdf http://localhost:5000/api/download/filename.pdf
```

## 源码版本使用

### 启动服务器

```bash
# 启动服务器
python -m file_preview.cli.main server

# 指定端口启动
python -m file_preview.cli.main server --port 8080

# 指定主机启动
python -m file_preview.cli.main server --host 0.0.0.0
```

### 转换文件

```bash
# 转换本地文件
python -m file_preview.cli.main convert /path/to/file.docx

# 转换网络文件
python -m file_preview.cli.main convert-url https://example.com/file.docx
```

## 使用示例

### 1. 转换并预览本地文件

```bash
# 启动服务器
file-preview server

# 在浏览器中访问
http://localhost:5000

# 上传文件并预览
# 或者使用 API
curl -X POST -F "file=@document.docx" http://localhost:5000/api/convert
```

### 2. 转换并预览网络文件

```bash
# 使用 API 转换网络文件
curl "http://localhost:5000/api/convert/url?url=https://example.com/document.docx"

# 在浏览器中预览
# 复制返回的预览 URL 并在浏览器中打开
```

### 3. 批量转换文件

```bash
# 使用脚本批量转换
for file in *.docx; do
  file-preview convert "$file"
done
```

### 4. 使用 Docker 部署

```bash
# 创建必要的目录
mkdir -p config cache download log convert

# 复制配置文件
cp config/config.yaml config/

# 启动服务
docker-compose up -d

# 访问服务
http://localhost:5000
```

## 支持的格式

File Preview 支持以下文件格式的预览：

- 文档格式：
  - Microsoft Word (.doc, .docx)
  - Microsoft Excel (.xls, .xlsx)
  - Microsoft PowerPoint (.ppt, .pptx)
  - PDF (.pdf)
  - 文本文件 (.txt)
  - Markdown (.md)

- 图片格式：
  - JPEG (.jpg, .jpeg)
  - PNG (.png)
  - GIF (.gif)
  - BMP (.bmp)
  - TIFF (.tiff)

## 常见问题

1. 文件无法预览
   - 检查文件格式是否支持
   - 检查文件是否损坏
   - 检查服务器日志

2. 转换失败
   - 检查文件大小是否超过限制
   - 检查服务器磁盘空间
   - 检查 LibreOffice 是否正常运行

3. 网络文件无法下载
   - 检查 URL 是否可访问
   - 检查网络连接
   - 检查防火墙设置

4. 性能问题
   - 增加服务器内存
   - 优化缓存设置
   - 定期清理缓存

## 下一步

- 查看 [配置说明](configuration.md) 了解详细配置选项
- 查看 [API 文档](../api/core.md) 了解 API 使用方法
- 查看 [开发文档](../developer/setup.md) 了解如何参与开发 