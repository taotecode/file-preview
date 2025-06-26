# 配置指南

## 配置文件

文件预览服务器使用YAML格式的配置文件。默认配置文件位于项目根目录下的`config.yaml`。您也可以通过环境变量`CONFIG_PATH`指定自定义配置文件路径。

## 基础配置项

### 服务器配置

```yaml
server:
  host: 0.0.0.0          # 服务器监听地址
  port: 5001             # 服务器监听端口
  debug: true            # 是否启用调试模式
  secret_key: "your_secret_key_here"  # Flask应用密钥，用于会话等
  allowed_origins:       # CORS允许的源
    - "http://localhost:3000"
    - "https://your-domain.com"
```

### 路径配置

```yaml
paths:
  root_dir: ""           # 应用根目录（留空表示自动检测）
  cache_dir: "tmp/file_preview/cache"       # 缓存目录
  download_dir: "tmp/file_preview/download" # 下载文件存储目录
  convert_dir: "tmp/file_preview/convert"   # 转换后文件存储目录
  log_dir: "tmp/file_preview/log"           # 日志目录
```

### 日志配置

```yaml
logging:
  level: "INFO"          # 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "file_preview.log"  # 日志文件名（相对于log_dir）
  max_size: 10           # 单个日志文件最大大小（MB）
  backup_count: 5        # 保留的日志文件数量
```

## 高级配置

### 文件转换配置

```yaml
converter:
  libreoffice:
    bin_path: "/Applications/LibreOffice.app/Contents/MacOS/soffice"  # LibreOffice可执行文件路径
    timeout: 60          # 转换超时时间（秒）
    retry_count: 3       # 失败重试次数
  pdf:
    resolution: 150      # PDF转图片分辨率
    quality: 90          # 图片质量（1-100）
  cache:
    enabled: true        # 是否启用缓存
    ttl: 604800          # 缓存过期时间（秒，默认7天）
```

### 任务队列配置

```yaml
task_queue:
  type: "redis"          # 队列类型: redis, local
  redis:
    host: "localhost"    # Redis服务器地址
    port: 6379           # Redis服务器端口
    db: 0                # Redis数据库
    password: ""         # Redis密码（如需）
  workers: 2             # 工作线程数
  task_timeout: 300      # 任务超时时间（秒）
```

### 安全配置

```yaml
security:
  max_file_size: 50      # 最大文件大小（MB）
  allowed_extensions:    # 允许的文件扩展名
    - ".pdf"
    - ".docx"
    - ".doc"
    - ".xlsx"
    - ".xls"
    - ".pptx"
    - ".ppt"
    - ".txt"
  api_tokens:            # API访问令牌列表
    - "your_api_token_1"
    - "your_api_token_2"
  rate_limit:
    enabled: true        # 是否启用速率限制
    requests: 100        # 时间窗口内允许的请求数
    window: 60           # 时间窗口大小（秒）
```

### URL配置

```yaml
urls:
  base_url: "http://localhost:5001"  # 应用基础URL（用于生成完整URL）
  preview_path: "/preview"           # 预览页面路径
  api_path: "/api"                   # API路径前缀
```

## 环境变量覆盖

您可以使用环境变量覆盖配置文件中的设置。环境变量名称应使用大写字母，并使用下划线替换点，前缀为`FILE_PREVIEW_`。例如：

```bash
# 设置服务器端口
export FILE_PREVIEW_SERVER_PORT=8080

# 设置Redis主机
export FILE_PREVIEW_TASK_QUEUE_REDIS_HOST=redis.example.com
```

## 配置示例

### 最小配置

```yaml
server:
  port: 5001
paths:
  root_dir: "/path/to/your/app"
converter:
  libreoffice:
    bin_path: "/usr/bin/libreoffice"
```

### 生产环境配置

```yaml
server:
  host: "0.0.0.0"
  port: 5001
  debug: false
  secret_key: "your_secure_secret_key"
  allowed_origins:
    - "https://your-production-domain.com"

paths:
  root_dir: "/var/www/file_preview"
  cache_dir: "/var/data/file_preview/cache"
  download_dir: "/var/data/file_preview/download"
  convert_dir: "/var/data/file_preview/convert"
  log_dir: "/var/log/file_preview"

logging:
  level: "WARNING"
  file: "file_preview.log"
  max_size: 50
  backup_count: 10

converter:
  libreoffice:
    bin_path: "/usr/bin/libreoffice"
    timeout: 120
  cache:
    enabled: true
    ttl: 2592000  # 30天

task_queue:
  type: "redis"
  redis:
    host: "redis.internal"
    port: 6379
    db: 0
    password: "your_redis_password"
  workers: 4

security:
  max_file_size: 20
  api_tokens:
    - "your_production_api_token"
  rate_limit:
    enabled: true
    requests: 50
    window: 60

urls:
  base_url: "https://preview.your-domain.com"
```

## 代理配置

如果您在反向代理后面运行服务器，请确保正确配置：

```yaml
server:
  proxy_fix:
    enabled: true
    x_for: 1
    x_proto: 1
    x_host: 1
    x_port: 0
    x_prefix: 0
```

## 配置验证

启动服务时，系统会验证配置文件的正确性。如果配置无效，服务将无法启动并显示错误消息。

您可以使用以下命令验证配置文件，而不启动服务：

```bash
python -m file_preview.utils.config_validator /path/to/your/config.yaml
``` 