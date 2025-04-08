# File Preview

文件预览服务，支持多种文件格式转换为 PDF 并在线预览。

## 功能特性

- 支持多种文档格式的预览（Word、Excel、PDF 等）
- 支持在线和本地文件的预览
- 提供 RESTful API 接口
- 支持命令行操作
- 可配置的缓存管理
- 跨平台支持（Windows、macOS、Linux）

## 安装

```bash
# 克隆项目
git clone https://github.com/taotecode/file-preview.git
cd file-preview

# 安装依赖
pip install -r requirements.txt
```

## 快速开始

### 使用 Docker

```bash
# 拉取最新版本
docker pull your-dockerhub-username/file-preview:latest

# 运行容器
docker run -d \
  -p 5000:5000 \
  -v /path/to/config.yaml:/app/config.yaml \
  -v /path/to/cache:/app/cache \
  -v /path/to/download:/app/download \
  -v /path/to/convert:/app/convert \
  -v /path/to/log:/app/log \
  your-dockerhub-username/file-preview:latest
```

### 使用二进制文件

1. 从 [Releases](https://github.com/your-username/file-preview/releases) 页面下载对应平台的二进制文件
2. 确保已安装 LibreOffice
3. 运行程序：

```bash
# 给予执行权限
chmod +x file-preview-*

# 运行服务
./file-preview-* server
```

## 构建说明

### 本地构建

```bash
# 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 运行构建脚本
./build.sh
```

### 发布新版本

1. 创建并推送标签：

```bash
git tag v1.0.0
git push origin v1.0.0
```

2. GitHub Actions 会自动：
   - 构建多平台 Docker 镜像
   - 发布到 Docker Hub
   - 构建二进制文件
   - 创建 GitHub Release

## 配置说明

配置文件 `config.yaml` 包含以下主要设置：

```yaml
server:
  host: 0.0.0.0
  port: 5000
  max_content_length: 100  # MB

directories:
  cache: cache
  download: download
  convert: convert
  log: log

conversion:
  supported_formats:
    - .doc
    - .docx
    - .xls
    - .xlsx
    - .ppt
    - .pptx
    - .txt
    - .pdf

cache:
  max_size: 1024  # MB
  retention_days: 7
```

## 支持的平台

- Linux (amd64, arm64)
- macOS (amd64, arm64)
- Docker (amd64, arm64)

## 文档

详细文档请参考 [docs/README.md](docs/README.md)

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。 