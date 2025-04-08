"""
命令行入口
"""

import click
from ..server.app import create_app
from ..utils.config import load_config

@click.group()
def cli():
    """文件预览工具"""
    pass

@cli.command()
def server():
    """启动 API 服务器"""
    app = create_app()
    config = load_config()
    app.run(
        host=config['server']['host'],
        port=config['server']['port']
    )

if __name__ == '__main__':
    cli() 