# 配置说明

本文档详细说明了 File Preview 的配置选项。您可以通过配置文件或环境变量来配置 File Preview。

## 配置文件

File Preview 使用 YAML 格式的配置文件。默认配置文件位于 `config/config.yaml`。

### 基本配置

```yaml
server:
  host: 0.0.0.0
  port: 5000
  max_content_length: 104857600  # 100MB

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
    - .md
    - .jpg
    - .jpeg
    - .png
    - .gif
    - .bmp
    - .tiff
  max_retries: 3
  timeout: 300  # 5分钟

cache:
  enabled: true
  max_size: 1073741824  # 1GB
  retention_days: 7

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: file_preview.log
```

### 配置说明

#### 服务器配置

- `host`: 服务器监听的主机地址
  - 默认值: `0.0.0.0`
  - 说明: 设置为 `0.0.0.0` 允许从任何 IP 访问

- `port`: 服务器监听的端口
  - 默认值: `5000`
  - 说明: 确保端口未被其他服务占用

- `max_content_length`: 最大文件大小（字节）
  - 默认值: `104857600` (100MB)
  - 说明: 限制上传文件的大小

#### 目录配置

- `cache`: 缓存目录
  - 默认值: `cache`
  - 说明: 存储转换后的文件缓存

- `download`: 下载目录
  - 默认值: `download`
  - 说明: 存储从网络下载的文件

- `convert`: 转换目录
  - 默认值: `convert`
  - 说明: 存储转换后的文件

- `log`: 日志目录
  - 默认值: `log`
  - 说明: 存储日志文件

#### 转换配置

- `supported_formats`: 支持的文件格式
  - 默认值: 见配置文件
  - 说明: 列出所有支持转换的文件格式

- `max_retries`: 最大重试次数
  - 默认值: `3`
  - 说明: 转换失败时的重试次数

- `timeout`: 转换超时时间（秒）
  - 默认值: `300`
  - 说明: 单个文件转换的最大时间

#### 缓存配置

- `enabled`: 是否启用缓存
  - 默认值: `true`
  - 说明: 控制是否使用缓存功能

- `max_size`: 最大缓存大小（字节）
  - 默认值: `1073741824` (1GB)
  - 说明: 限制缓存目录的总大小

- `retention_days`: 缓存保留天数
  - 默认值: `7`
  - 说明: 缓存文件的最大保留时间

#### 日志配置

- `level`: 日志级别
  - 默认值: `INFO`
  - 可选值: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
  - 说明: 控制日志的详细程度

- `format`: 日志格式
  - 默认值: `"%(asctime)s - %(name)s - %(levelname)s - %(message)s"`
  - 说明: 控制日志的输出格式

- `file`: 日志文件
  - 默认值: `file_preview.log`
  - 说明: 日志文件的名称

## 环境变量

您也可以通过环境变量来配置 File Preview。环境变量的优先级高于配置文件。

### 服务器配置

- `HOST`: 服务器监听的主机地址
- `PORT`: 服务器监听的端口
- `MAX_CONTENT_LENGTH`: 最大文件大小（字节）

### 目录配置

- `CACHE_DIR`: 缓存目录
- `DOWNLOAD_DIR`: 下载目录
- `CONVERT_DIR`: 转换目录
- `LOG_DIR`: 日志目录

### 转换配置

- `MAX_RETRIES`: 最大重试次数
- `TIMEOUT`: 转换超时时间（秒）

### 缓存配置

- `CACHE_ENABLED`: 是否启用缓存
- `CACHE_MAX_SIZE`: 最大缓存大小（字节）
- `CACHE_RETENTION_DAYS`: 缓存保留天数

### 日志配置

- `LOG_LEVEL`: 日志级别
- `LOG_FORMAT`: 日志格式
- `LOG_FILE`: 日志文件

## Docker 配置

在 Docker 环境中，您可以通过以下方式配置：

1. 使用环境变量：
```bash
docker run -d \
  -e HOST=0.0.0.0 \
  -e PORT=5000 \
  -e MAX_CONTENT_LENGTH=104857600 \
  taotecode/file-preview:latest
```

2. 使用配置文件：
```bash
docker run -d \
  -v /path/to/config.yaml:/app/config/config.yaml \
  taotecode/file-preview:latest
```

3. 使用 docker-compose：
```yaml
version: '3'
services:
  file-preview:
    image: taotecode/file-preview:latest
    environment:
      - HOST=0.0.0.0
      - PORT=5000
      - MAX_CONTENT_LENGTH=104857600
    volumes:
      - ./config:/app/config
```

## 配置示例

### 开发环境配置

```yaml
server:
  host: 127.0.0.1
  port: 5000
  max_content_length: 52428800  # 50MB

logging:
  level: DEBUG
```

### 生产环境配置

```yaml
server:
  host: 0.0.0.0
  port: 80
  max_content_length: 104857600  # 100MB

cache:
  enabled: true
  max_size: 2147483648  # 2GB
  retention_days: 30

logging:
  level: INFO
  file: /var/log/file_preview.log
```

### 高并发配置

```yaml
server:
  host: 0.0.0.0
  port: 80
  max_content_length: 209715200  # 200MB

conversion:
  max_retries: 5
  timeout: 600  # 10分钟

cache:
  enabled: true
  max_size: 5368709120  # 5GB
  retention_days: 15
```

## 配置验证

您可以使用以下命令验证配置：

```bash
# 检查配置文件语法
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

# 检查环境变量
env | grep -i file_preview
```

## 配置更新

更新配置后，需要重启服务才能生效：

```bash
# 二进制版本
file-preview server --reload

# Docker 版本
docker-compose restart

# 源码版本
python -m file_preview.cli.main server --reload
```

## 故障排除

1. 配置不生效
   - 检查配置文件路径
   - 检查环境变量优先级
   - 检查配置文件语法

2. 目录权限问题
   - 确保目录存在
   - 确保有读写权限
   - 检查 SELinux/AppArmor 设置

3. 缓存问题
   - 检查磁盘空间
   - 检查目录权限
   - 检查缓存配置

4. 日志问题
   - 检查日志目录权限
   - 检查日志级别设置
   - 检查日志文件大小 