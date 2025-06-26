# 文件预览服务器快速入门

## 概述

文件预览服务器是一个用于在线预览各种格式文件的工具，支持PDF、Word、Excel等多种常见文档格式。本指南将帮助您快速设置并开始使用该服务。

## 环境要求

- Python 3.9+
- LibreOffice (用于文档转换)
- Redis (可选，用于任务队列)
- 操作系统: Windows/Linux/macOS

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/file_previews.git
cd file_previews
```

### 2. 创建虚拟环境

```bash
python -m venv venv
```

- Windows:
  ```bash
  venv\Scripts\activate
  ```
- Linux/macOS:
  ```bash
  source venv/bin/activate
  ```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 安装LibreOffice

- Windows: 从[官方网站](https://www.libreoffice.org/download/download/)下载安装包
- macOS: `brew install --cask libreoffice`
- Linux (Ubuntu): `sudo apt install libreoffice`

### 5. 创建必要的目录

```bash
mkdir -p tmp/file_preview/{cache,download,convert,log}
```

## 配置

### 基础配置

编辑`config.ini`文件（如果不存在，请创建一个）:

```ini
[server]
host = 0.0.0.0
port = 5001
debug = True

[paths]
cache_dir = tmp/file_preview/cache
download_dir = tmp/file_preview/download
convert_dir = tmp/file_preview/convert
log_dir = tmp/file_preview/log

[libreoffice]
# Windows示例
# bin_path = C:\\Program Files\\LibreOffice\\program\\soffice.exe
# macOS示例
bin_path = /Applications/LibreOffice.app/Contents/MacOS/soffice
# Linux示例
# bin_path = /usr/bin/libreoffice
```

### 高级配置

对于生产环境，您可能需要配置Redis任务队列：

```ini
[redis]
host = localhost
port = 6379
db = 0
```

## 启动服务器

```bash
python run.py
```

服务器将在`http://localhost:5001`启动。

## 使用方法

### 1. 上传并预览文件

```bash
# 上传文件并获取任务ID
curl -X POST -F "file=@/path/to/your/document.docx" "http://localhost:5001/api/convert"
```

响应示例:
```json
{
  "status": "success",
  "task_id": "abc123def456",
  "message": "文件上传成功，正在转换",
  "preview_url": "http://localhost:5001/preview?task_id=abc123def456",
  "download_url": "http://localhost:5001/api/files/download?task_id=abc123def456"
}
```

### 2. 通过URL转换并预览文件

```bash
curl -X GET "http://localhost:5001/api/convert?url=https://example.com/document.pdf"
```

### 3. 直接预览文件

上传并转换成功后，使用以下URL在浏览器中预览：

```
http://localhost:5001/preview?file_id=文件ID
```

或使用任务ID（自动等待转换完成）：

```
http://localhost:5001/preview?task_id=任务ID
```

## API参考

详细的API文档请参考：

- [API总览](../api/index.md)
- [文件转换API](../api/convert.md)
- [文件预览API](../api/preview.md)

## 常见问题

### 1. 转换失败

- 检查LibreOffice是否正确安装
- 确保文件格式受支持
- 检查日志文件（在`tmp/file_preview/log`目录下）

### 2. 无法预览文件

- 确认文件已成功转换
- 检查文件ID或任务ID是否正确
- 检查浏览器是否支持PDF预览

### 3. 如何删除过期文件？

系统会自动清理7天前的临时文件，您也可以手动运行清理脚本：

```bash
python scripts/cleanup.py
```

## 下一步

- [配置指南](./configuration.md)
- [部署到生产环境](./deployment.md)
- [开发者文档](../developer/index.md) 