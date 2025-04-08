# 使用多阶段构建
# 第一阶段：构建阶段
FROM --platform=$BUILDPLATFORM python:3.10-slim as builder

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 使用 PyInstaller 构建二进制文件
RUN pip install pyinstaller
RUN pyinstaller --clean --onefile \
    --add-data "config.yaml:." \
    --add-data "file_preview:file_preview" \
    file_preview/cli/main.py

# 第二阶段：运行阶段
FROM --platform=$TARGETPLATFORM python:3.10-slim

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 从构建阶段复制二进制文件
COPY --from=builder /app/dist/main /app/file-preview
COPY config.yaml /app/

# 创建必要的目录
RUN mkdir -p /app/cache /app/download /app/log /app/convert

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 5000

# 设置入口点
ENTRYPOINT ["/app/file-preview"]
CMD ["server"] 