"""
缓存测试
"""

import os
import time
import pytest
from unittest.mock import patch, MagicMock
from file_preview.core.cache import CacheManager

def test_cache_init(test_config: dict):
    """
    测试缓存初始化
    
    Args:
        test_config: 测试配置
    """
    # 创建缓存
    cache = CacheManager(test_config)
    
    # 验证配置
    assert cache.cache_dir == test_config['directories']['cache']
    assert cache.retention_days == test_config['cache']['retention_days']
    assert cache.max_size == test_config['cache']['max_size'] * 1024 * 1024  # 转换为字节
    
    # 验证目录已创建
    assert os.path.exists(cache.cache_dir)

def test_cache_key(test_file: str, test_config: dict):
    """
    测试缓存键生成
    
    Args:
        test_file: 测试文件路径
        test_config: 测试配置
    """
    # 创建缓存
    cache = CacheManager(test_config)
    
    # 生成缓存键
    cache_key = cache.get_cache_key(test_file)
    
    # 验证缓存键
    assert isinstance(cache_key, str)
    assert len(cache_key) == 32  # MD5 哈希长度

def test_cache_path(test_config: dict):
    """
    测试缓存路径生成
    
    Args:
        test_config: 测试配置
    """
    # 创建缓存
    cache = CacheManager(test_config)
    
    # 生成缓存路径
    cache_key = 'test_key'
    cache_path = cache.get_cache_path(cache_key)
    
    # 验证缓存路径
    assert cache_path == os.path.join(test_config['directories']['cache'], f"{cache_key}.pdf")

def test_cache_operations(test_file: str, test_pdf: str, test_config: dict):
    """
    测试缓存操作
    
    Args:
        test_file: 测试文件路径
        test_pdf: 测试 PDF 文件路径
        test_config: 测试配置
    """
    # 创建缓存
    cache = CacheManager(test_config)
    
    # 测试缓存不存在
    assert not cache.exists(test_file)
    assert cache.get(test_file) is None
    
    # 添加文件到缓存
    cache_path = cache.put(test_file, test_pdf)
    
    # 验证缓存
    assert cache.exists(test_file)
    assert cache.get(test_file) == cache_path
    assert os.path.exists(cache_path)
    
    # 验证文件内容
    with open(cache_path, 'r') as f:
        assert f.read() == 'PDF content'

def test_cache_cleanup_expired(test_file: str, test_pdf: str, test_config: dict):
    """
    测试过期缓存清理
    
    Args:
        test_file: 测试文件路径
        test_pdf: 测试 PDF 文件路径
        test_config: 测试配置
    """
    # 创建缓存
    cache = CacheManager(test_config)
    
    # 添加文件到缓存
    cache_path = cache.put(test_file, test_pdf)
    
    # 修改文件的访问和修改时间为7天前
    access_time = time.time() - (test_config['cache']['retention_days'] + 1) * 24 * 60 * 60
    os.utime(cache_path, (access_time, access_time))
    
    # 清理过期缓存
    cache.cleanup()
    
    # 验证缓存已删除
    assert not cache.exists(test_file)
    assert cache.get(test_file) is None

def test_cache_cleanup_size(test_file: str, test_pdf: str, test_config: dict):
    """
    测试缓存大小清理
    
    Args:
        test_file: 测试文件路径
        test_pdf: 测试 PDF 文件路径
        test_config: 测试配置
    """
    # 创建缓存
    cache = CacheManager(test_config)
    
    # 添加大文件到缓存
    large_file = os.path.join(test_config['directories']['cache'], 'large.pdf')
    with open(large_file, 'w') as f:
        f.write('0' * (test_config['cache']['max_size'] * 1024 * 1024 + 1))
    
    # 添加文件到缓存
    cache_path = cache.put(test_file, test_pdf)
    
    # 清理缓存
    cache.cleanup()
    
    # 验证缓存大小限制
    assert not os.path.exists(large_file)
    assert os.path.exists(cache_path) 