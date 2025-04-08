"""
测试配置
"""

import os
import pytest
import tempfile
import shutil
from typing import Dict, Any, Generator

@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """
    创建临时目录
    
    Yields:
        临时目录路径
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def test_config(temp_dir: str) -> Dict[str, Any]:
    """
    测试配置
    
    Args:
        temp_dir: 临时目录路径
        
    Returns:
        测试配置字典
    """
    return {
        'directories': {
            'cache': os.path.join(temp_dir, 'cache'),
            'download': os.path.join(temp_dir, 'download'),
            'convert': os.path.join(temp_dir, 'convert'),
            'log': os.path.join(temp_dir, 'log')
        },
        'server': {
            'host': '127.0.0.1',
            'port': 5000
        },
        'cache': {
            'retention_days': 7,
            'max_size': 1024
        },
        'logging': {
            'level': 'DEBUG',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'performance': {
            'max_workers': 4,
            'download_timeout': 30,
            'keep_original_name': True,
            'enable_multithreading': True,
            'worker_processes': 2
        },
        'conversion': {
            'libreoffice_path': '/usr/bin/libreoffice',
            'office_path': '/Applications/Microsoft Office',
            'timeout': 300,
            'retry_times': 3,
            'supported_formats': ['.doc', '.docx', '.xls', '.xlsx', '.txt']
        }
    }

@pytest.fixture
def test_file(temp_dir: str) -> Generator[str, None, None]:
    """
    创建测试文件
    
    Args:
        temp_dir: 临时目录路径
        
    Yields:
        测试文件路径
    """
    file_path = os.path.join(temp_dir, 'test.docx')
    with open(file_path, 'w') as f:
        f.write('Test content')
    yield file_path
    if os.path.exists(file_path):
        os.remove(file_path)

@pytest.fixture
def test_pdf(temp_dir: str) -> Generator[str, None, None]:
    """
    创建测试 PDF 文件
    
    Args:
        temp_dir: 临时目录路径
        
    Yields:
        测试 PDF 文件路径
    """
    file_path = os.path.join(temp_dir, 'test.pdf')
    with open(file_path, 'w') as f:
        f.write('PDF content')
    yield file_path
    if os.path.exists(file_path):
        os.remove(file_path) 