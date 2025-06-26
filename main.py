#!/usr/bin/env python3
"""
命令行主入口
"""

import argparse
import os
import sys
import logging

# 获取应用根目录
if getattr(sys, 'frozen', False):
    # 打包后的路径
    app_root = os.path.dirname(sys.executable)
else:
    # 开发环境下的路径
    app_root = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, app_root)

import click
from file_preview.utils.config import load_config
from file_preview.utils.logger import setup_logger
from file_preview.cli.commands import convert, server
from file_preview.server.app import create_app

def check_config(config):
    """检查配置是否有效"""
    is_valid = True
    message = "配置有效"
    
    # 检查必须的配置项
    required_sections = ["server", "directories", "conversion"]
    for section in required_sections:
        if section not in config:
            return False, f"配置缺少 '{section}' 部分"
    
    # 检查服务器配置
    if "host" not in config["server"] or "port" not in config["server"]:
        # 添加默认值
        if "host" not in config["server"]:
            config["server"]["host"] = "0.0.0.0"
            message += ", 使用默认主机"
        if "port" not in config["server"]:
            config["server"]["port"] = 5001
            message += ", 使用默认端口"
    
    # 检查目录配置
    required_dirs = ["cache", "download", "convert", "log"]
    for dir_name in required_dirs:
        if dir_name not in config["directories"]:
            # 添加默认值
            if dir_name == "log":
                config["directories"]["log"] = "./logs"
            elif dir_name == "cache":
                config["directories"]["cache"] = "./cache"
            elif dir_name == "download":
                config["directories"]["download"] = "./download"
            elif dir_name == "convert":
                config["directories"]["convert"] = "./convert"
            
            message += f", 添加默认 {dir_name} 目录"
    
    # 确保转换配置正确
    required_conversion = ["libreoffice_path", "timeout", "retry_times"]
    for item in required_conversion:
        if item not in config["conversion"]:
            if item == "libreoffice_path":
                config["conversion"]["libreoffice_path"] = "libreoffice"
            elif item == "timeout":
                config["conversion"]["timeout"] = 60
            elif item == "retry_times":
                config["conversion"]["retry_times"] = 3
            
            message += f", 添加默认 {item} 值"
    
    return is_valid, message

@click.group()
@click.option('--config', '-c', help='配置文件路径')
@click.pass_context
def cli(ctx, config):
    """
    File Preview 命令行工具
    """
    # 如果未指定配置文件，则使用默认路径
    if config is None:
        config = os.path.join(app_root, 'config.yaml')
    
    # 检查配置文件是否存在
    if not os.path.exists(config):
        click.echo(f"错误: 配置文件不存在: {config}")
        ctx.exit(1)
    
    try:
        # 加载配置
        config_data = load_config(config)
        
        # 检查配置有效性
        is_valid, message = check_config(config_data)
        if not is_valid:
            click.echo(f"错误: {message}")
            ctx.exit(1)
        
        # 设置日志记录器
        logger = setup_logger(config_data)
        
        # 保存到上下文
        ctx.obj = {
            'config': config_data,
            'logger': logger
        }
    except Exception as e:
        click.echo(f"配置加载失败: {str(e)}")
        ctx.exit(1)

# 添加子命令
cli.add_command(convert)
cli.add_command(server)

def run_server(host='0.0.0.0', port=5001, debug=False, use_reloader=True):
    """启动文件预览服务器"""
    try:
        # 加载配置
        config_file = os.path.join(app_root, 'config.yaml')
        config = load_config(config_file)
        
        # 检查配置有效性
        is_valid, message = check_config(config)
        if not is_valid:
            print(f"错误: {message}")
            return
        
        # 设置日志记录器
        logger = setup_logger(config)
        
        # 设置环境变量
        os.environ['FLASK_APP'] = 'file_preview.server.app'
        if debug:
            os.environ['FLASK_ENV'] = 'development'
            os.environ['FLASK_DEBUG'] = '1'
        
        print(f"服务启动在 http://{host}:{port}")
        print(f"调试模式: {'开启' if debug else '关闭'}")
        print(f"热重载: {'关闭' if not use_reloader else '开启'}")
        
        # 创建应用 - 传递配置文件路径而不是配置对象
        app = create_app(config_file)
        
        # 启动服务器
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=use_reloader
        )
    except Exception as e:
        print(f"服务启动失败: {str(e)}")
        sys.exit(1)

def main():
    """程序主入口点"""
    # 如果没有参数或只有一个参数且不是子命令，则显示帮助信息或直接启动服务器
    if len(sys.argv) <= 1 or (len(sys.argv) == 2 and sys.argv[1] not in ['convert', 'server', '--help', '-h']):
        parser = argparse.ArgumentParser(description='文件预览服务')
        parser.add_argument('--host', default='0.0.0.0', help='服务主机地址 (默认: 0.0.0.0)')
        parser.add_argument('--port', type=int, default=5001, help='服务端口 (默认: 5001)')
        parser.add_argument('--debug', action='store_true', help='启用调试模式')
        parser.add_argument('--no-reload', action='store_true', help='禁用热重载')
        
        # 解析命令行参数（仅处理已提供的参数）
        args, _ = parser.parse_known_args()
        
        # 启动服务器
        run_server(
            host=args.host,
            port=args.port,
            debug=args.debug,
            use_reloader=not args.no_reload
        )
    else:
        # 使用Click命令行界面
        cli()

if __name__ == '__main__':
    main() 