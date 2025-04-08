# 安装指南

File Preview 提供了多种安装方式，包括二进制安装、Docker 安装和源码安装。您可以根据自己的需求选择合适的安装方式。

## 二进制安装

### 下载二进制文件

1. 访问 [GitHub Releases](https://github.com/taotecode/file-preview/releases) 页面
2. 根据您的操作系统和架构下载对应的二进制文件：
   - macOS (Intel): `file-preview-macos-amd64`
   - macOS (Apple Silicon): `file-preview-macos-arm64`
   - Linux (Intel): `file-preview-linux-amd64`
   - Linux (ARM): `file-preview-linux-arm64`

### 安装步骤

1. 下载二进制文件后，添加执行权限：
```bash
chmod +x file-preview-*
```

2. 将二进制文件移动到系统路径（可选）：
```bash
sudo mv file-preview-* /usr/local/bin/file-preview
```

3. 验证安装：
```bash
file-preview --version
```

## Docker 安装

### 拉取镜像

```bash
docker pull taotecode/file-preview:latest
```

### 运行容器

1. 基本运行：
```bash
docker run -d \
  -p 5000:5000 \
  -v /path/to/config:/app/config \
  -v /path/to/cache:/app/cache \
  -v /path/to/download:/app/download \
  -v /path/to/log:/app/log \
  -v /path/to/convert:/app/convert \
  taotecode/file-preview:latest
```

2. 使用自定义配置：
```bash
docker run -d \
  -p 5000:5000 \
  -v /path/to/custom-config.yaml:/app/config/config.yaml \
  -v /path/to/cache:/app/cache \
  -v /path/to/download:/app/download \
  -v /path/to/log:/app/log \
  -v /path/to/convert:/app/convert \
  taotecode/file-preview:latest
```

3. 使用环境变量配置：
```bash
docker run -d \
  -p 5000:5000 \
  -e HOST=0.0.0.0 \
  -e PORT=5000 \
  -e MAX_CONTENT_LENGTH=104857600 \
  -v /path/to/cache:/app/cache \
  -v /path/to/download:/app/download \
  -v /path/to/log:/app/log \
  -v /path/to/convert:/app/convert \
  taotecode/file-preview:latest
```

### Docker Compose 部署

创建 `docker-compose.yml` 文件：

```yaml
version: '3'
services:
  file-preview:
    image: taotecode/file-preview:latest
    ports:
      - "5000:5000"
    volumes:
      - ./config:/app/config
      - ./cache:/app/cache
      - ./download:/app/download
      - ./log:/app/log
      - ./convert:/app/convert
    environment:
      - HOST=0.0.0.0
      - PORT=5000
      - MAX_CONTENT_LENGTH=104857600
    restart: unless-stopped
```

启动服务：
```bash
docker-compose up -d
```

## 源码安装

### 克隆仓库

```bash
git clone https://github.com/taotecode/file-preview.git
cd file-preview
```

### 安装依赖

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
.\venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

### 运行服务

```bash
python -m file_preview.cli.main server
```

## 系统要求

### 二进制版本
- 操作系统：Windows、macOS、Linux
- 架构：amd64、arm64

### Docker 版本
- Docker Engine 20.10.0 或更高版本
- Docker Compose 2.0.0 或更高版本（可选）

### 源码版本
- Python 3.10 或更高版本
- pip 20.0.0 或更高版本
- 操作系统：Windows、macOS、Linux

## 目录结构

安装完成后，建议创建以下目录结构：

```
file-preview/
├── config/
│   └── config.yaml
├── cache/
├── download/
├── log/
└── convert/
```

## 配置说明

安装完成后，您需要配置 `config.yaml` 文件。详细配置说明请参考 [配置说明](configuration.md)。

## 常见问题

1. 权限问题
   - 确保所有挂载的目录具有正确的读写权限
   - Docker 容器默认以非 root 用户运行

2. 端口冲突
   - 如果 5000 端口被占用，可以通过环境变量或配置文件修改端口

3. 存储空间
   - 确保有足够的磁盘空间用于缓存和转换文件
   - 定期清理缓存文件

4. 网络问题
   - 确保服务器可以访问互联网（用于下载网络文件）
   - 检查防火墙设置

## 更新说明

### 二进制版本
1. 下载新版本的二进制文件
2. 替换旧版本文件
3. 重启服务

### Docker 版本
```bash
docker pull taotecode/file-preview:latest
docker-compose down
docker-compose up -d
```

### 源码版本
```bash
git pull
pip install -r requirements.txt
``` 