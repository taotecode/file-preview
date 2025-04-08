"""
文件转换器测试
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from file_preview.core.converter import FileConverter

def test_converter_init(test_config: dict):
    """
    测试转换器初始化
    
    Args:
        test_config: 测试配置
    """
    # 创建转换器
    converter = FileConverter(test_config)
    
    # 验证配置
    assert converter.convert_dir == test_config['directories']['convert']
    assert converter.timeout == test_config['conversion']['timeout']
    assert converter.retry_times == test_config['conversion']['retry_times']
    assert converter.libreoffice_path == test_config['conversion']['libreoffice_path']
    
    # 验证目录已创建
    assert os.path.exists(converter.convert_dir)

@patch('subprocess.Popen')
@patch('os.path.exists')
@patch('file_preview.core.converter.is_supported_format')
@patch('file_preview.core.converter.generate_output_path')
def test_convert_success(mock_generate_path, mock_is_supported, mock_exists, mock_popen, test_file, test_config):
    """
    测试转换成功

    Args:
        mock_generate_path: 模拟的 generate_output_path
        mock_is_supported: 模拟的 is_supported_format
        mock_exists: 模拟的 os.path.exists
        mock_popen: 模拟的 Popen
        test_file: 测试文件路径
        test_config: 测试配置
    """
    # 设置模拟返回值
    mock_process = MagicMock()
    mock_process.communicate.return_value = (b'', b'')
    mock_process.returncode = 0
    mock_popen.return_value = mock_process

    # 模拟文件存在
    def exists_side_effect(path):
        if path == test_file:
            return True
        if path.endswith('.pdf'):
            return True  # 转换后文件存在
        return False
    mock_exists.side_effect = exists_side_effect

    # 模拟文件格式支持
    mock_is_supported.return_value = True

    # 模拟输出路径生成
    output_path = os.path.join(test_config['directories']['convert'], 'test.pdf')
    mock_generate_path.return_value = output_path

    # 创建转换器
    converter = FileConverter(test_config)

    # 转换文件
    result_path = converter.convert(test_file)

    # 验证转换命令
    expected_cmd = [
        test_config['conversion']['libreoffice_path'],
        '--headless',
        '--convert-to',
        'pdf',
        '--outdir',
        test_config['directories']['convert'],
        test_file
    ]
    mock_popen.assert_not_called()  # 因为文件已经存在，所以不应该调用转换命令
    assert result_path == output_path

@patch('subprocess.Popen')
def test_convert_failure(mock_popen: MagicMock, test_file: str, test_config: dict):
    """
    测试转换失败
    
    Args:
        mock_popen: 模拟的 Popen
        test_file: 测试文件路径
        test_config: 测试配置
    """
    # 设置模拟返回值
    mock_process = MagicMock()
    mock_process.communicate.return_value = (b'', b'Error')
    mock_process.returncode = 1
    mock_popen.return_value = mock_process
    
    # 创建转换器
    converter = FileConverter(test_config)
    
    # 转换文件
    output_path = converter.convert(test_file)
    
    # 验证转换失败
    assert output_path is None
    assert mock_popen.call_count == test_config['conversion']['retry_times']

@patch('subprocess.Popen')
def test_convert_timeout(mock_popen: MagicMock, test_file: str, test_config: dict):
    """
    测试转换超时
    
    Args:
        mock_popen: 模拟的 Popen
        test_file: 测试文件路径
        test_config: 测试配置
    """
    # 设置模拟超时
    mock_process = MagicMock()
    mock_process.communicate.side_effect = TimeoutError()
    mock_popen.return_value = mock_process
    
    # 创建转换器
    converter = FileConverter(test_config)
    
    # 转换文件
    output_path = converter.convert(test_file)
    
    # 验证转换超时
    assert output_path is None
    assert mock_popen.call_count == test_config['conversion']['retry_times']
    assert mock_process.kill.call_count == test_config['conversion']['retry_times'] 