# File Preview 文档

File Preview 是一个强大的文件预览工具，支持将 Word、Excel 等文档转换为 PDF 并在线预览。

## 快速开始

### 直接执行（无需编译）

1. 启动服务器：
```bash
python -m file_preview.cli.main server
```

2. 转换本地文件：
```bash
python -m file_preview.cli.main convert /path/to/file.docx --output /path/to/output.pdf
```

3. 转换网络文件：
```bash
python -m file_preview.cli.main convert-url https://example.com/file.docx --output /path/to/output.pdf
```

4. 清理缓存：
```bash
python -m file_preview.cli.main cleanup
```

## 文档目录

### 用户指南
- [安装指南](user/installation.md) - 如何安装和配置 File Preview
- [快速开始](user/quickstart.md) - 快速上手使用 File Preview
- [配置说明](user/configuration.md) - 详细的配置选项说明

### API 文档
- [核心模块](api/core.md) - 核心功能模块的 API 文档
- [服务器模块](api/server.md) - 服务器模块的 API 文档
- [命令行接口](api/cli.md) - 命令行工具的 API 文档

### 开发文档
- [开发环境搭建](development/setup.md) - 如何搭建开发环境
- [项目架构](development/architecture.md) - 项目架构说明
- [贡献指南](development/contributing.md) - 如何参与项目开发

## 功能特性

- 支持多种文档格式的预览（Word、Excel、PDF 等）
- 支持在线和本地文件的预览
- 提供 RESTful API 接口
- 支持命令行操作
- 可配置的缓存管理
- 跨平台支持（Windows、macOS、Linux）

## 系统要求

- Python 3.6 或更高版本
- 操作系统：Windows、macOS、Linux
- 依赖项：
  - Flask >= 2.0.0
  - requests >= 2.25.0
  - docx2pdf >= 0.1.7
  - pandas >= 1.1.0
  - openpyxl >= 3.0.7
  - pypdf >= 3.0.0

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](../LICENSE) 文件。 