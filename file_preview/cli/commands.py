"""
命令行命令实现
"""

import os
import click
from typing import Optional
from ..core.converter import FileConverter
from ..core.downloader import FileDownloader
from ..core.cache import CacheManager
from ..utils.file import get_file_info, is_supported_format

@click.command()
@click.argument('file_path')
@click.option('--url', '-u', help='文件 URL')
@click.option('--output', '-o', help='输出目录')
@click.option('--no-cache', is_flag=True, help='不使用缓存')
@click.pass_context
def convert(ctx, file_path: str, url: Optional[str], output: Optional[str], no_cache: bool):
    """
    转换文件为 PDF
    
    FILE_PATH: 本地文件路径或文件 URL
    """
    config = ctx.obj['config']
    logger = ctx.obj['logger']
    
    try:
        # 初始化组件
        converter = FileConverter(config)
        downloader = FileDownloader(config)
        cache_manager = CacheManager(config)
        
        # 处理网络文件
        if url:
            logger.info(f"下载文件: {url}")
            file_path = downloader.download(url)
            if not file_path:
                logger.error("下载文件失败")
                return
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return
        
        # 检查文件格式
        if not is_supported_format(file_path, config):
            logger.error(f"不支持的文件格式: {get_file_info(file_path)['extension']}")
            return
        
        # 检查缓存
        if not no_cache and cache_manager.exists(file_path):
            logger.info("使用缓存文件")
            pdf_path = cache_manager.get(file_path)
        else:
            # 转换文件
            logger.info(f"转换文件: {file_path}")
            pdf_path = converter.convert(file_path, output)
            if not pdf_path:
                logger.error("转换文件失败")
                return
            
            # 添加到缓存
            if not no_cache:
                logger.info("添加到缓存")
                cache_manager.put(file_path, pdf_path)
        
        # 输出结果
        logger.info(f"转换完成: {pdf_path}")
        click.echo(f"PDF 文件已保存到: {pdf_path}")
        
    except Exception as e:
        logger.error(f"转换失败: {str(e)}")
        click.echo(f"错误: {str(e)}")
    finally:
        # 清理下载的临时文件
        if url and file_path and os.path.exists(file_path):
            downloader.cleanup(file_path)

@click.command()
@click.option('--host', '-h', help='服务器主机地址')
@click.option('--port', '-p', type=int, help='服务器端口')
@click.option('--debug', is_flag=True, help='启用调试模式')
@click.option('--no-reload', is_flag=True, help='禁用热重载')
@click.pass_context
def server(ctx, host: Optional[str], port: Optional[int], debug: bool = False, no_reload: bool = False):
    """
    启动预览服务器
    """
    config = ctx.obj['config']
    logger = ctx.obj['logger']
    
    try:
        from ..server.app import create_app
        
        # 获取当前工作目录作为根目录
        root_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # 默认配置文件路径
        config_path = os.path.join(root_dir, 'config.yaml')
        
        # 应用命令行参数覆盖配置
        server_host = host or config['server']['host']
        server_port = port or config['server']['port']
        
        # 启动信息
        logger.info(f"启动服务器: {server_host}:{server_port}")
        click.echo(f"服务启动在 http://{server_host}:{server_port}")
        click.echo(f"调试模式: {'开启' if debug else '关闭'}")
        click.echo(f"热重载: {'关闭' if no_reload else '开启'}")
        
        # 设置环境变量
        os.environ['FLASK_APP'] = 'file_preview.server.app'
        if debug:
            os.environ['FLASK_ENV'] = 'development'
            os.environ['FLASK_DEBUG'] = '1'
        
        # 创建应用，传递配置文件路径
        app = create_app(config_path)
        
        # 启动服务器
        app.run(
            host=server_host,
            port=server_port,
            debug=debug,
            use_reloader=not no_reload
        )
        
    except Exception as e:
        logger.error(f"启动服务器失败: {str(e)}")
        click.echo(f"错误: {str(e)}") 