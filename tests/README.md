# 文件预览服务测试说明

这个目录包含用于测试文件预览服务的测试脚本。

## 自动测试（pytest）

使用pytest进行自动化测试：

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动服务（在一个终端中）
python -m file_preview.cli.main server

# 在另一个终端中运行测试
pytest tests/test_server.py -v
```

## 手动测试

手动测试脚本提供了更详细的输出和测试流程：

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动服务（在一个终端中）
python -m file_preview.cli.main server

# 在另一个终端中运行手动测试
python tests/test_server_manual.py
```

## 远程URL测试

专门测试远程URL的下载、转换和预览：

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动服务（在一个终端中）
python -m file_preview.cli.main server

# 在另一个终端中测试特定文件类型
python tests/test_remote_url.py doc   # 测试DOC文件
python tests/test_remote_url.py docx  # 测试DOCX文件
python tests/test_remote_url.py xls   # 测试XLS文件
python tests/test_remote_url.py xlsx  # 测试XLSX文件
python tests/test_remote_url.py all   # 测试所有文件类型
```

## 测试功能点

这些测试脚本会测试以下功能点：

1. 文件上传
2. 文件下载
3. 文件转换
4. 文件预览

## 测试文件

测试使用以下文件类型：

- DOC 文件 (.doc)
- DOCX 文件 (.docx)
- XLS 文件 (.xls)
- XLSX 文件 (.xlsx)

测试会使用本地`test_files`目录中的文件和远程URL中的文件进行测试。

## 测试结果

手动测试会输出详细的测试过程和结果，包括：

- 服务器状态检查
- 文件上传/URL下载状态
- 转换任务状态
- 文件下载状态
- 文件预览状态

如果测试过程中出现任何错误，会显示相应的错误信息。 