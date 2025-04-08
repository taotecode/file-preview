#!/bin/bash

# 设置变量
VERSION=$(git describe --tags --abbrev=0)
DOCKER_USERNAME="your-dockerhub-username"

# 构建多平台 Docker 镜像
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t $DOCKER_USERNAME/file-preview:latest \
  -t $DOCKER_USERNAME/file-preview:$VERSION \
  --push .

# 构建本地二进制文件
pyinstaller --clean --onefile \
  --add-data "config.yaml:." \
  --add-data "file_preview:file_preview" \
  file_preview/cli/main.py

# 重命名二进制文件
mv dist/main dist/file-preview-$VERSION-$(uname -s)-$(uname -m) 