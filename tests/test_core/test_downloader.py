"""
下载器测试
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from file_preview.core.downloader import FileDownloader

def test_downloader_init(test_config: dict):
    """
    测试下载器初始化
    
    Args:
        test_config: 测试配置
    """
    # 创建下载器
    downloader = FileDownloader(test_config)
    
    # 验证配置
    assert downloader.download_dir == test_config['directories']['download']
    assert downloader.timeout == test_config['performance']['download_timeout']
    
    # 验证目录已创建
    assert os.path.exists(downloader.download_dir)

@patch('requests.get')
def test_download_success(mock_get: MagicMock, test_config: dict):
    """
    测试下载成功
    
    Args:
        mock_get: 模拟的 requests.get
        test_config: 测试配置
    """
    # 设置模拟返回值
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_content.return_value = [b'Test content']
    mock_response.headers = {'Content-Type': 'application/pdf'}
    mock_get.return_value = mock_response
    
    # 创建下载器
    downloader = FileDownloader(test_config)
    
    # 下载文件
    url = 'http://example.com/test.pdf'
    output_path = downloader.download(url)
    
    # 验证下载
    mock_get.assert_called_once_with(url, timeout=test_config['performance']['download_timeout'], stream=True)
    assert output_path is not None
    assert os.path.exists(output_path)
    assert os.path.basename(output_path).endswith('.pdf')
    
    # 验证文件内容
    with open(output_path, 'rb') as f:
        content = f.read()
    assert content == b'Test content'

@patch('requests.get')
def test_download_failure(mock_get: MagicMock, test_config: dict):
    """
    测试下载失败
    
    Args:
        mock_get: 模拟的 requests.get
        test_config: 测试配置
    """
    # 设置模拟返回值
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    
    # 创建下载器
    downloader = FileDownloader(test_config)
    
    # 下载文件
    url = 'http://example.com/test.pdf'
    output_path = downloader.download(url)
    
    # 验证下载失败
    mock_get.assert_called_once_with(url, timeout=test_config['performance']['download_timeout'], stream=True)
    assert output_path is None

@patch('requests.get')
def test_download_timeout(mock_get: MagicMock, test_config: dict):
    """
    测试下载超时
    
    Args:
        mock_get: 模拟的 requests.get
        test_config: 测试配置
    """
    # 设置模拟超时
    mock_get.side_effect = TimeoutError()
    
    # 创建下载器
    downloader = FileDownloader(test_config)
    
    # 下载文件
    url = 'http://example.com/test.pdf'
    output_path = downloader.download(url)
    
    # 验证下载超时
    mock_get.assert_called_once_with(url, timeout=test_config['performance']['download_timeout'], stream=True)
    assert output_path is None

def test_cleanup(test_config: dict):
    """
    测试清理功能
    
    Args:
        test_config: 测试配置
    """
    # 创建下载器
    downloader = FileDownloader(test_config)
    
    # 创建测试文件
    test_file = os.path.join(downloader.download_dir, 'test.pdf')
    with open(test_file, 'w') as f:
        f.write('Test content')
    
    # 验证文件存在
    assert os.path.exists(test_file)
    
    # 清理文件
    downloader.cleanup(test_file)
    
    # 验证文件已删除
    assert not os.path.exists(test_file) 