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
@click.option('--port', '-p', help='服务器端口')
@click.pass_context
def server(ctx, host: Optional[str], port: Optional[int]):
    """
    启动预览服务器
    """
    config = ctx.obj['config']
    logger = ctx.obj['logger']
    
    try:
        from ..server.app import create_app
        
        # 更新配置
        if host:
            config['server']['host'] = host
        if port:
            config['server']['port'] = port
        
        # 创建应用
        app = create_app(config)
        
        # 启动服务器
        logger.info(f"启动服务器: {config['server']['host']}:{config['server']['port']}")
        app.run(
            host=config['server']['host'],
            port=config['server']['port'],
            debug=False
        )
        
    except Exception as e:
        logger.error(f"启动服务器失败: {str(e)}")
        click.echo(f"错误: {str(e)}") 