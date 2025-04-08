"""
文件处理工具测试
"""

import os
import pytest
from file_preview.utils.file import get_file_info, is_supported_format, generate_output_path

def test_get_file_info(test_file: str):
    """
    测试获取文件信息
    
    Args:
        test_file: 测试文件路径
    """
    # 获取文件信息
    info = get_file_info(test_file)
    
    # 验证文件信息
    assert info['name'] == 'test.docx'
    assert info['size'] > 0
    assert info['path'] == test_file
    assert info['extension'] == '.docx'

def test_get_file_info_not_found():
    """
    测试获取不存在的文件信息
    """
    with pytest.raises(FileNotFoundError):
        get_file_info('nonexistent.docx')

def test_is_supported_format(test_file: str, test_config: dict):
    """
    测试检查文件格式是否支持
    
    Args:
        test_file: 测试文件路径
        test_config: 测试配置
    """
    # 测试支持的格式
    assert is_supported_format(test_file, test_config) == True  # .docx 在支持列表中
    
    # 测试不支持的格式
    test_file_unsupported = test_file.replace('.docx', '.xyz')
    assert is_supported_format(test_file_unsupported, test_config) == False

def test_generate_output_path(test_file: str, test_config: dict):
    """
    测试生成输出文件路径
    
    Args:
        test_file: 测试文件路径
        test_config: 测试配置
    """
    # 测试保留原文件名
    output_path = generate_output_path(test_config['directories']['convert'], test_file, keep_original_name=True)
    assert output_path.endswith('test.pdf')
    assert os.path.dirname(output_path) == test_config['directories']['convert']
    
    # 测试不保留原文件名
    output_path = generate_output_path(test_config['directories']['convert'], test_file, keep_original_name=False)
    assert output_path.endswith('.pdf')
    assert os.path.dirname(output_path) == test_config['directories']['convert']
    assert len(os.path.basename(output_path)) == 36 + 4  # UUID长度 + .pdf 