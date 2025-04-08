# 开发环境搭建

本文档将指导您如何搭建 File Preview 的开发环境。

## 系统要求

- Python 3.10 或更高版本
- Git
- LibreOffice（用于文档转换）
- Docker（可选，用于测试）
- Docker Compose（可选，用于测试）

## 开发环境搭建

### 1. 克隆仓库

```bash
git clone https://github.com/taotecode/file-preview.git
cd file-preview
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate

# Windows
.\venv\Scripts\activate
```

### 3. 安装依赖

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 安装项目依赖
pip install -r requirements.txt
```

### 4. 安装 LibreOffice

#### macOS

```bash
# 使用 Homebrew 安装
brew install libreoffice
```

#### Ubuntu/Debian

```bash
# 使用 apt 安装
sudo apt update
sudo apt install libreoffice
```

#### Windows

1. 访问 [LibreOffice 官网](https://www.libreoffice.org/download/download/)
2. 下载并安装最新版本

### 5. 配置开发环境

1. 复制配置文件：

```bash
cp config/config.yaml.example config/config.yaml
```

2. 修改配置文件：

```yaml
server:
  host: 127.0.0.1
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
  level: DEBUG
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: file_preview.log
```

### 6. 创建必要的目录

```bash
mkdir -p cache download log convert
```

## 运行测试

### 1. 运行单元测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_core/test_converter.py

# 运行测试并生成覆盖率报告
pytest --cov=file_preview
```

### 2. 运行代码检查

```bash
# 运行 flake8
flake8

# 运行 mypy
mypy file_preview

# 运行 black
black file_preview tests

# 运行 isort
isort file_preview tests
```

## 开发工作流

### 1. 创建新分支

```bash
git checkout -b feature/your-feature-name
```

### 2. 开发新功能

1. 编写代码
2. 添加测试
3. 运行测试
4. 提交更改

```bash
git add .
git commit -m "feat: add new feature"
```

### 3. 创建 Pull Request

1. 推送分支到远程仓库
```bash
git push origin feature/your-feature-name
```

2. 在 GitHub 上创建 Pull Request

### 4. 代码审查

1. 等待代码审查
2. 根据反馈修改代码
3. 更新 Pull Request

## 调试

### 1. 使用日志

```python
import logging

logger = logging.getLogger('file_preview')
logger.debug('Debug message')
logger.info('Info message')
logger.warning('Warning message')
logger.error('Error message')
```

### 2. 使用调试器

```bash
# 使用 pdb
python -m pdb -m file_preview.cli.main server

# 使用 ipdb
pip install ipdb
python -m ipdb -m file_preview.cli.main server
```

### 3. 使用 IDE 调试

1. 配置 IDE 的调试器
2. 设置断点
3. 启动调试会话

## 构建文档

### 1. 安装文档工具

```bash
pip install sphinx sphinx-rtd-theme
```

### 2. 构建文档

```bash
cd docs
make html
```

### 3. 查看文档

```bash
open _build/html/index.html  # macOS
start _build/html/index.html  # Windows
xdg-open _build/html/index.html  # Linux
```

## Docker 开发环境

### 1. 构建开发镜像

```bash
docker build -t file-preview-dev -f Dockerfile.dev .
```

### 2. 运行开发容器

```bash
docker run -it --rm \
  -v $(pwd):/app \
  -p 5000:5000 \
  file-preview-dev
```

### 3. 使用 Docker Compose

```bash
docker-compose -f docker-compose.dev.yml up
```

## 常见问题

### 1. 依赖安装失败

- 确保使用最新版本的 pip
- 尝试使用 `--no-cache-dir` 选项
- 检查网络连接

### 2. 测试失败

- 检查测试环境配置
- 确保所有依赖已安装
- 检查日志输出

### 3. 文档构建失败

- 确保安装了所有文档依赖
- 检查 Sphinx 配置
- 检查文档语法

### 4. Docker 构建失败

- 检查 Dockerfile 语法
- 确保所有文件都存在
- 检查网络连接

## 下一步

- 查看 [项目架构](architecture.md) 了解项目结构
- 查看 [贡献指南](contributing.md) 了解如何参与开发
- 查看 [API 文档](../api/core.md) 了解 API 使用方法 