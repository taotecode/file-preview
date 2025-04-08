#!/usr/bin/env python3
"""
命令行主入口
"""

import os
import sys

# 获取应用根目录
if getattr(sys, 'frozen', False):
    # 打包后的路径
    app_root = os.path.dirname(sys.executable)
else:
    # 开发环境下的路径
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, app_root)

import click
from file_preview.utils.config import load_config
from file_preview.utils.logger import setup_logger
from file_preview.cli.commands import convert, server

@click.group()
@click.option('--config', '-c', help='配置文件路径')
@click.pass_context
def main(ctx, config):
    """
    File Preview 命令行工具
    """
    # 如果未指定配置文件，则使用默认路径
    if config is None:
        config = os.path.join(app_root, 'config.yaml')
    
    # 加载配置
    ctx.obj = {
        'config': load_config(config),
        'logger': setup_logger(load_config(config))
    }

# 添加子命令
main.add_command(convert)
main.add_command(server)

if __name__ == '__main__':
    main() 