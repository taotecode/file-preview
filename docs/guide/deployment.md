# 部署指南

本指南将帮助您在各种环境中部署文件预览服务器，包括开发环境、测试环境和生产环境。

## 开发环境部署

### 直接运行

开发环境下，您可以直接运行应用程序：

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动服务器
python -m file_preview.app
```

服务器将在 `http://localhost:5001` 启动，并启用调试模式。

### 使用Docker进行开发

```bash
# 构建开发镜像
docker build -t file-preview-dev -f Dockerfile.dev .

# 运行容器
docker run -p 5001:5001 -v $(pwd):/app file-preview-dev
```

## 测试环境部署

### 使用Gunicorn

```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:5001 'file_preview.app:create_app()'
```

### 使用Docker Compose

创建`docker-compose.yml`文件：

```yaml
version: '3'

services:
  app:
    build: .
    ports:
      - "5001:5001"
    environment:
      - CONFIG_PATH=/app/config/test.yaml
    volumes:
      - ./config:/app/config
      - ./data:/app/data
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

启动服务：

```bash
docker-compose up -d
```

## 生产环境部署

### 前期准备

1. 为生产环境创建专用配置文件，确保：
   - 禁用调试模式
   - 使用强密钥
   - 配置适当的日志级别
   - 设置适当的CORS策略

2. 确保服务器满足所有依赖项要求：
   - Python 3.9+
   - LibreOffice
   - Redis (如果使用)

### 使用Supervisor管理进程

1. 安装Supervisor：

```bash
apt-get install supervisor
```

2. 创建配置文件 `/etc/supervisor/conf.d/file-preview.conf`：

```ini
[program:file-preview]
command=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5001 'file_preview.app:create_app()'
directory=/path/to/file_preview
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/file_preview/supervisor.log
environment=CONFIG_PATH="/etc/file_preview/config.yaml"

[program:file-preview-worker]
command=/path/to/venv/bin/python -m file_preview.worker
directory=/path/to/file_preview
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/file_preview/worker.log
environment=CONFIG_PATH="/etc/file_preview/config.yaml"
```

3. 启动服务：

```bash
supervisorctl reread
supervisorctl update
supervisorctl start file-preview
supervisorctl start file-preview-worker
```

### Nginx配置

1. 安装Nginx：

```bash
apt-get install nginx
```

2. 创建配置文件 `/etc/nginx/sites-available/file-preview.conf`：

```nginx
server {
    listen 80;
    server_name preview.yourdomain.com;

    # 重定向HTTP到HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name preview.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 静态文件
    location /static {
        alias /path/to/file_preview/static;
        expires 30d;
    }
    
    # 应用服务器代理
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持（如需）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 120s;
    }
    
    # 大文件上传配置
    client_max_body_size 100M;
    
    # 访问日志
    access_log /var/log/nginx/file_preview_access.log;
    error_log /var/log/nginx/file_preview_error.log;
}
```

3. 启用站点：

```bash
ln -s /etc/nginx/sites-available/file-preview.conf /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Docker Swarm部署

1. 创建`docker-compose.prod.yml`：

```yaml
version: '3.8'

services:
  app:
    image: file-preview:1.0.0
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
      update_config:
        parallelism: 1
        delay: 10s
      resources:
        limits:
          cpus: '1'
          memory: 1G
    environment:
      - CONFIG_PATH=/config/prod.yaml
    volumes:
      - config_vol:/config
      - data_vol:/data
    ports:
      - "5001:5001"
    networks:
      - preview-net
      
  worker:
    image: file-preview:1.0.0
    command: python -m file_preview.worker
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
    environment:
      - CONFIG_PATH=/config/prod.yaml
    volumes:
      - config_vol:/config
      - data_vol:/data
    networks:
      - preview-net
  
  redis:
    image: redis:6-alpine
    deploy:
      placement:
        constraints: [node.role == manager]
    volumes:
      - redis_data:/data
    networks:
      - preview-net

volumes:
  config_vol:
    driver: local
  data_vol:
    driver: local
  redis_data:
    driver: local

networks:
  preview-net:
    driver: overlay
```

2. 初始化Swarm并部署：

```bash
# 初始化Swarm
docker swarm init

# 部署服务
docker stack deploy -c docker-compose.prod.yml file-preview
```

### Kubernetes部署

1. 创建配置映射 `config-map.yaml`：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: file-preview-config
data:
  config.yaml: |
    server:
      host: "0.0.0.0"
      port: 5001
      debug: false
    
    # 其他配置项...
```

2. 创建部署文件 `deployment.yaml`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: file-preview
  labels:
    app: file-preview
spec:
  replicas: 3
  selector:
    matchLabels:
      app: file-preview
  template:
    metadata:
      labels:
        app: file-preview
    spec:
      containers:
      - name: app
        image: your-registry/file-preview:1.0.0
        ports:
        - containerPort: 5001
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
          requests:
            cpu: "500m"
            memory: "512Mi"
        volumeMounts:
        - name: config-volume
          mountPath: /config
        - name: data-volume
          mountPath: /data
        env:
        - name: CONFIG_PATH
          value: "/config/config.yaml"
        livenessProbe:
          httpGet:
            path: /api/stats
            port: 5001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/stats
            port: 5001
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config-volume
        configMap:
          name: file-preview-config
      - name: data-volume
        persistentVolumeClaim:
          claimName: file-preview-data
---
apiVersion: v1
kind: Service
metadata:
  name: file-preview-service
spec:
  selector:
    app: file-preview
  ports:
  - port: 80
    targetPort: 5001
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: file-preview-ingress
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
spec:
  rules:
  - host: preview.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: file-preview-service
            port:
              number: 80
  tls:
  - hosts:
    - preview.yourdomain.com
    secretName: preview-tls-secret
```

3. 应用配置：

```bash
kubectl apply -f config-map.yaml
kubectl apply -f deployment.yaml
```

## 安全最佳实践

1. **配置SSL/TLS**：始终使用HTTPS保护流量。

2. **定期更新依赖**：保持所有依赖项是最新的。

3. **最小化权限**：使用非root用户运行服务。

4. **保护API**：使用API令牌或其他认证机制。

5. **设置资源限制**：防止资源耗尽攻击。

6. **备份数据**：定期备份重要数据。

7. **监控系统**：实施日志监控和告警系统。

## 部署检查清单

- [ ] 创建适当的配置文件
- [ ] 确保所有目录具有正确的权限
- [ ] 验证LibreOffice路径配置
- [ ] 配置日志轮转
- [ ] 设置监控和告警
- [ ] 测试备份和恢复流程
- [ ] 实施SSL/TLS证书
- [ ] 配置防火墙规则
- [ ] 验证所有API端点的安全性
- [ ] 确保Redis（如使用）受到保护

## 故障排除

### 常见问题

1. **服务器无法启动**
   - 检查配置文件语法
   - 验证目录权限
   - 查看日志文件

2. **文件转换失败**
   - 确认LibreOffice安装正确
   - 检查临时目录权限
   - 增加转换超时时间

3. **服务器响应缓慢**
   - 增加工作线程数
   - 监控内存使用情况
   - 检查网络延迟

### 日志分析

使用以下命令查看日志：

```bash
# Supervisor日志
tail -f /var/log/file_preview/supervisor.log

# Nginx访问日志
tail -f /var/log/nginx/file_preview_access.log

# 应用程序日志
tail -f /var/log/file_preview/file_preview.log
```

## 性能调优

1. **增加工作线程**：根据服务器CPU核心数调整工作线程数。

2. **优化Nginx配置**：启用压缩、缓存和HTTP/2。

3. **Redis持久化**：在生产环境中配置适当的Redis持久化选项。

4. **监控资源使用**：使用工具如Prometheus和Grafana监控系统性能。

5. **文件缓存**：调整缓存配置以平衡性能和存储空间。 