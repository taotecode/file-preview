# 部署指南

## 系统要求

- Python 3.8 或更高版本
- LibreOffice 7.0 或更高版本
- 至少 2GB 可用内存
- 至少 1GB 可用磁盘空间

## 安装方式

### 1. 直接执行（无需安装）

直接从源码目录执行：
```bash
# 克隆仓库
git clone https://github.com/taotecode/file-preview.git
cd file-preview

# 安装依赖
pip install -r requirements.txt

# 启动服务器
python -m file_preview.cli.main server
```

### 2. 使用 pip 安装

```bash
pip install file-preview
```

### 3. 从源码安装

```bash
git clone https://github.com/taotecode/file-preview.git
cd file-preview
pip install -e .
```

## 配置

1. 创建配置文件 `config.yaml`：

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
  max_size: 1024  # MB

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

2. 确保所有配置的目录存在并有适当的权限：

```bash
mkdir -p /path/to/cache /path/to/download /path/to/convert /path/to/log
chmod 755 /path/to/cache /path/to/download /path/to/convert /path/to/log
```

## 运行服务

### 1. 直接执行（无需安装）

```bash
python -m file_preview.cli.main server
```

### 2. 命令行方式（安装后）

```bash
file-preview server --config /path/to/config.yaml
```

### 3. 使用 systemd（Linux）

1. 创建服务文件 `/etc/systemd/system/file-preview.service`：

```ini
[Unit]
Description=File Preview Service
After=network.target

[Service]
User=your_user
Group=your_group
WorkingDirectory=/path/to/working/dir
ExecStart=/usr/bin/python3 -m file_preview.cli.main server
Restart=always

[Install]
WantedBy=multi-user.target
```

2. 启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable file-preview
sudo systemctl start file-preview
```

### 4. 使用 Docker

1. 构建镜像：

```bash
docker build -t file-preview .
```

2. 运行容器：

```bash
docker run -d \
  -p 5000:5000 \
  -v /path/to/config.yaml:/app/config.yaml \
  -v /path/to/cache:/app/cache \
  -v /path/to/download:/app/download \
  -v /path/to/convert:/app/convert \
  -v /path/to/log:/app/log \
  file-preview
```

## 监控和维护

### 日志查看

```bash
tail -f /path/to/log/file_preview.log
```

### 缓存清理

#### 直接执行：
```bash
python -m file_preview.cli.main cleanup
```

#### 使用安装后的命令：
```bash
file-preview cleanup --config /path/to/config.yaml
```

### 性能监控

使用以下命令监控服务性能：

```bash
# 查看进程状态
ps aux | grep file-preview

# 查看内存使用
top -p $(pgrep -f file-preview)

# 查看磁盘使用
du -sh /path/to/cache
```

## 故障排除

1. 检查日志文件中的错误信息
2. 确保 LibreOffice 已正确安装并可执行
3. 验证所有配置目录的权限
4. 检查网络连接（如果使用 URL 转换功能）
5. 确保有足够的磁盘空间

## 安全建议

1. 在生产环境中使用 HTTPS
2. 限制文件上传大小
3. 定期清理缓存文件
4. 使用防火墙限制访问
5. 定期更新依赖包 