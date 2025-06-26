# 文件预览系统安装部署指南

## 1. 系统要求

### 1.1 服务器要求

- **操作系统**：
  - Linux（推荐Ubuntu 20.04+或CentOS 8+）
  - macOS 10.15+
  - Windows 10/Server 2019+
- **CPU**：双核处理器或更高配置（推荐4核+）
- **内存**：最低4GB，推荐8GB+
- **硬盘**：至少10GB可用空间，用于应用和缓存文件
- **网络**：稳定的网络连接，推荐10Mbps+带宽

### 1.2 软件依赖

- **Python**：Python 3.8+ (推荐Python 3.10+)
- **数据库**：SQLite（内置）或MySQL 5.7+/PostgreSQL 12+（可选）
- **Web服务器**：Nginx/Apache（生产环境推荐）
- **其他依赖**：
  - LibreOffice 7.0+（用于Office文档转换）
  - Poppler-utils（用于PDF处理）
  - FFmpeg（用于视频文件处理，可选）
  - ImageMagick（用于图像处理）

## 2. 安装步骤

### 2.1 基础环境准备

#### Ubuntu/Debian系统

```bash
# 更新系统包
sudo apt update
sudo apt upgrade -y

# 安装Python和pip
sudo apt install -y python3 python3-pip python3-venv

# 安装依赖软件
sudo apt install -y libreoffice poppler-utils imagemagick ffmpeg

# 安装开发工具
sudo apt install -y build-essential python3-dev
```

#### CentOS/RHEL系统

```bash
# 更新系统包
sudo yum update -y

# 安装Python和pip
sudo yum install -y python3 python3-pip python3-devel

# 安装依赖软件
sudo yum install -y libreoffice poppler-tools ImageMagick ffmpeg

# 安装开发工具
sudo yum groupinstall -y "Development Tools"
```

#### macOS系统

```bash
# 使用Homebrew安装依赖
brew update
brew install python libreoffice poppler imagemagick ffmpeg
```

### 2.2 获取源码

```bash
# 克隆代码仓库
git clone https://github.com/yourusername/file_previews.git
cd file_previews

# 或者下载并解压源码包
wget https://github.com/yourusername/file_previews/archive/refs/heads/main.zip
unzip main.zip
cd file_previews-main
```

### 2.3 设置Python虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate
# Windows
# venv\Scripts\activate

# 安装依赖包
pip install -r requirements.txt
```

### 2.4 初始化配置

```bash
# 复制配置文件模板
cp config.yaml.example config.yaml

# 编辑配置文件
# 根据您的环境修改配置参数
nano config.yaml  # 或使用任何文本编辑器
```

主要配置项说明：

- `server`: 服务器相关配置，包括端口、主机等
- `storage`: 存储路径配置，包括上传文件、转换结果等
- `database`: 数据库连接配置
- `converter`: 文件转换相关配置
- `log`: 日志配置

### 2.5 初始化数据库

```bash
# 运行初始化脚本
python initialize_db.py
```

### 2.6 测试安装

```bash
# 启动开发服务器
python -m file_preview.server.app

# 测试服务是否正常运行
# 打开浏览器访问 http://localhost:5001
```

## 3. 生产环境部署

### 3.1 使用Gunicorn部署

```bash
# 安装Gunicorn
pip install gunicorn

# 启动Gunicorn服务器
gunicorn -w 4 -b 0.0.0.0:5001 file_preview.server.app:app
```

### 3.2 Nginx配置

创建Nginx配置文件：

```bash
sudo nano /etc/nginx/sites-available/file_preview
```

添加以下配置：

```nginx
server {
    listen 80;
    server_name your_domain.com;  # 替换为您的域名

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        client_max_body_size 100M;  # 上传文件大小限制
    }

    location /static {
        alias /path/to/file_previews/static;  # 替换为静态文件实际路径
        expires 30d;
    }
}
```

启用配置并重启Nginx：

```bash
sudo ln -s /etc/nginx/sites-available/file_preview /etc/nginx/sites-enabled/
sudo nginx -t  # 测试配置
sudo systemctl restart nginx
```

### 3.3 设置Systemd服务（Linux）

创建服务文件：

```bash
sudo nano /etc/systemd/system/file_preview.service
```

添加以下内容：

```ini
[Unit]
Description=File Preview System
After=network.target

[Service]
User=www-data  # 替换为运行服务的用户
Group=www-data
WorkingDirectory=/path/to/file_previews  # 替换为实际路径
Environment="PATH=/path/to/file_previews/venv/bin"
ExecStart=/path/to/file_previews/venv/bin/gunicorn -w 4 -b 127.0.0.1:5001 file_preview.server.app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启用并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable file_preview
sudo systemctl start file_preview
sudo systemctl status file_preview  # 检查服务状态
```

### 3.4 使用Docker部署

如果您偏好使用Docker，可以按照以下步骤操作：

#### 3.4.1 使用提供的Dockerfile

```bash
# 构建Docker镜像
docker build -t file_preview_system .

# 运行容器
docker run -d --name file_preview \
  -p 5001:5001 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config.yaml:/app/config.yaml \
  file_preview_system
```

#### 3.4.2 使用Docker Compose

创建`docker-compose.yml`文件：

```yaml
version: '3'
services:
  file_preview:
    build: .
    container_name: file_preview
    ports:
      - "5001:5001"
    volumes:
      - ./data:/app/data
      - ./config.yaml:/app/config.yaml
    restart: unless-stopped
```

启动服务：

```bash
docker-compose up -d
```

## 4. 高级配置

### 4.1 数据库设置

默认情况下，系统使用SQLite作为数据库。在生产环境中，建议使用MySQL或PostgreSQL：

#### 4.1.1 MySQL配置

```yaml
# 在config.yaml中配置MySQL
database:
  type: mysql
  host: localhost
  port: 3306
  user: dbuser
  password: dbpassword
  database: file_preview_db
```

#### 4.1.2 PostgreSQL配置

```yaml
# 在config.yaml中配置PostgreSQL
database:
  type: postgresql
  host: localhost
  port: 5432
  user: dbuser
  password: dbpassword
  database: file_preview_db
```

### 4.2 文件存储配置

系统默认将文件存储在本地文件系统中。您可以配置不同的存储后端：

#### 4.2.1 本地文件系统

```yaml
storage:
  type: local
  upload_dir: /path/to/uploads
  cache_dir: /path/to/cache
  convert_dir: /path/to/converted
  temp_dir: /path/to/temp
```

#### 4.2.2 S3兼容存储（可选）

```yaml
storage:
  type: s3
  endpoint: https://s3.amazonaws.com
  region: us-east-1
  bucket: your-bucket-name
  access_key: your-access-key
  secret_key: your-secret-key
  prefix: file_preview/  # 可选前缀
```

### 4.3 安全设置

#### 4.3.1 HTTPS配置

在Nginx配置中启用HTTPS：

```nginx
server {
    listen 443 ssl;
    server_name your_domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... 其他配置与HTTP相同
}
```

#### 4.3.2 基本身份验证

在`config.yaml`中启用基本身份验证：

```yaml
server:
  # ... 其他设置
  auth:
    enabled: true
    type: basic
    users:
      - username: admin
        password: your_hashed_password
      - username: user
        password: another_hashed_password
```

### 4.4 性能优化

#### 4.4.1 缓存设置

```yaml
cache:
  type: redis  # 或 memcached
  host: localhost
  port: 6379
  db: 0
  # password: your_redis_password  # 如果需要
  ttl: 86400  # 缓存过期时间（秒）
```

#### 4.4.2 文件转换优化

```yaml
converter:
  workers: 4  # 并行转换工作进程数
  timeout: 300  # 转换超时时间（秒）
  retry: 2  # 转换失败重试次数
  memory_limit: 1024  # 每个转换任务的内存限制（MB）
```

## 5. 升级与维护

### 5.1 系统升级

```bash
# 进入项目目录
cd /path/to/file_previews

# 拉取最新代码
git pull

# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt

# 执行数据库迁移（如果有）
python migrate_db.py

# 重启服务
sudo systemctl restart file_preview
```

### 5.2 日常维护

#### 5.2.1 日志管理

系统日志位于配置文件指定的位置，默认为`logs/`目录。建议设置日志轮转：

```bash
# 安装logrotate（如果尚未安装）
sudo apt install logrotate  # Ubuntu/Debian
sudo yum install logrotate  # CentOS/RHEL

# 创建logrotate配置
sudo nano /etc/logrotate.d/file_preview
```

添加以下配置：

```
/path/to/file_previews/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
```

#### 5.2.2 缓存清理

定期清理临时文件和过期缓存：

```bash
# 创建清理脚本
nano /path/to/file_previews/scripts/clean_cache.sh
```

脚本内容：

```bash
#!/bin/bash
# 清理7天前的临时文件
find /path/to/file_previews/data/temp -type f -mtime +7 -delete
# 清理30天前的转换文件（如果不需要长期保存）
find /path/to/file_previews/data/converted -type f -mtime +30 -delete
```

设置执行权限并添加到crontab：

```bash
chmod +x /path/to/file_previews/scripts/clean_cache.sh
(crontab -l ; echo "0 2 * * * /path/to/file_previews/scripts/clean_cache.sh") | crontab -
```

### 5.3 备份策略

#### 5.3.1 数据库备份

```bash
# 创建备份脚本
nano /path/to/file_previews/scripts/backup_db.sh
```

对于SQLite数据库：

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p $BACKUP_DIR
# 备份SQLite数据库
sqlite3 /path/to/file_previews/data/file_preview.db ".backup '$BACKUP_DIR/file_preview_$TIMESTAMP.db'"
# 保留最近30天的备份
find $BACKUP_DIR -name "file_preview_*.db" -type f -mtime +30 -delete
```

对于MySQL数据库：

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_USER="dbuser"
DB_PASS="dbpassword"
DB_NAME="file_preview_db"
mkdir -p $BACKUP_DIR
# 备份MySQL数据库
mysqldump -u$DB_USER -p$DB_PASS $DB_NAME > $BACKUP_DIR/file_preview_$TIMESTAMP.sql
# 压缩备份
gzip $BACKUP_DIR/file_preview_$TIMESTAMP.sql
# 保留最近30天的备份
find $BACKUP_DIR -name "file_preview_*.sql.gz" -type f -mtime +30 -delete
```

设置执行权限并添加到crontab：

```bash
chmod +x /path/to/file_previews/scripts/backup_db.sh
(crontab -l ; echo "0 3 * * * /path/to/file_previews/scripts/backup_db.sh") | crontab -
```

#### 5.3.2 配置文件备份

定期备份配置文件和自定义数据：

```bash
# 创建备份脚本
nano /path/to/file_previews/scripts/backup_config.sh
```

脚本内容：

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups/config"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p $BACKUP_DIR
# 备份配置文件
cp /path/to/file_previews/config.yaml $BACKUP_DIR/config_$TIMESTAMP.yaml
# 保留最近10个版本
ls -t $BACKUP_DIR/config_*.yaml | tail -n +11 | xargs -r rm
```

## 6. 故障排除

### 6.1 常见问题

#### 6.1.1 服务无法启动

检查日志文件：

```bash
tail -n 100 /path/to/file_previews/logs/error.log
```

常见原因：
- 配置文件格式错误
- 数据库连接失败
- 端口冲突
- 权限问题

解决方案：
- 验证配置文件格式是否正确
- 检查数据库连接信息
- 确认端口是否被其他应用占用
- 检查文件和目录权限

#### 6.1.2 文件转换失败

检查转换日志：

```bash
tail -n 100 /path/to/file_previews/logs/converter.log
```

常见原因：
- LibreOffice安装不完整或错误
- 文件格式不受支持或已损坏
- 系统资源不足
- 转换超时

解决方案：
- 重新安装或修复LibreOffice
- 检查文件是否可以正常打开
- 增加系统资源或减少并行任务数
- 在配置中增加转换超时时间

#### 6.1.3 上传文件失败

常见原因：
- 文件大小超出限制
- 临时目录权限不足
- 磁盘空间不足

解决方案：
- 在Nginx配置中增加`client_max_body_size`
- 检查并修正目录权限
- 清理磁盘空间或迁移到更大的存储设备

### 6.2 日志分析

系统的主要日志文件：

- `logs/app.log` - 应用程序主日志
- `logs/error.log` - 错误日志
- `logs/access.log` - 访问日志
- `logs/converter.log` - 文件转换日志
- `logs/task.log` - 任务处理日志

使用以下命令分析日志中的错误：

```bash
# 查找错误信息
grep -i "error" /path/to/file_previews/logs/error.log

# 查找警告信息
grep -i "warning" /path/to/file_previews/logs/app.log

# 查找特定API的请求
grep "/api/convert" /path/to/file_previews/logs/access.log
```

### 6.3 性能问题

#### 6.3.1 系统负载高

检查系统资源使用情况：

```bash
# 安装监控工具
sudo apt install htop iotop

# 查看系统负载和进程
htop

# 查看磁盘I/O
sudo iotop
```

优化建议：
- 增加服务器CPU和内存
- 调整转换工作进程数量
- 使用SSD存储提高I/O性能
- 分离应用服务器和数据库服务器

#### 6.3.2 响应时间长

检查网络和应用性能：

```bash
# 网络延迟测试
ping -c 10 your_domain.com

# Web服务器性能测试
ab -n 100 -c 10 http://your_domain.com/
```

优化建议：
- 启用内容缓存
- 优化数据库查询
- 使用CDN加速静态内容
- 实施请求限流

## 7. 联系支持

如果您遇到无法解决的问题，请通过以下方式获取支持：

- **技术支持邮箱**: support@example.com
- **问题报告**: https://github.com/yourusername/file_previews/issues
- **文档网站**: https://docs.example.com/file_previews
- **社区论坛**: https://forum.example.com/file_previews 