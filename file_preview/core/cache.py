"""
缓存管理器
"""

import os
import hashlib
import shutil
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class CacheManager:
    """
    缓存管理器，用于管理文件转换的缓存
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化缓存管理器
        
        Args:
            config: 配置字典
        """
        self.cache_dir = config['directories']['cache']
        self.max_size = config['cache']['max_size'] * 1024 * 1024  # 转换为字节
        self.retention_days = config['cache']['retention_days']
        
        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 清理过期缓存
        self.cleanup()
    
    def get_cache_key(self, file_path: str) -> str:
        """
        生成缓存键
        
        Args:
            file_path: 文件路径
            
        Returns:
            缓存键
        """
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash
    
    def get_cache_path(self, cache_key: str) -> str:
        """
        获取缓存文件路径
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存文件路径
        """
        return os.path.join(self.cache_dir, f"{cache_key}.pdf")
    
    def exists(self, file_path: str) -> bool:
        """
        检查文件是否已缓存
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否已缓存
        """
        cache_key = self.get_cache_key(file_path)
        cache_path = self.get_cache_path(cache_key)
        return os.path.exists(cache_path)
    
    def get(self, file_path: str) -> Optional[str]:
        """
        获取缓存文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            缓存文件路径，如果不存在则返回 None
        """
        cache_key = self.get_cache_key(file_path)
        cache_path = self.get_cache_path(cache_key)
        return cache_path if os.path.exists(cache_path) else None
    
    def put(self, source_path: str, target_path: str) -> str:
        """
        将文件添加到缓存
        
        Args:
            source_path: 源文件路径
            target_path: 目标文件路径
            
        Returns:
            缓存文件路径
        """
        # 生成缓存键
        cache_key = self.get_cache_key(source_path)
        cache_path = self.get_cache_path(cache_key)

        # 如果缓存不存在，复制文件到缓存
        if not os.path.exists(cache_path):
            shutil.copy2(target_path, cache_path)

        return cache_path
    
    def cleanup(self):
        """
        清理缓存目录
        - 删除过期文件
        - 如果缓存大小超过限制，删除最旧的文件直到缓存大小小于限制
        """
        # 删除过期文件
        now = time.time()
        for file_name in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, file_name)
            if os.path.isfile(file_path):
                # 检查文件是否过期
                if now - os.path.getmtime(file_path) > self.retention_days * 24 * 3600:
                    os.remove(file_path)

        # 如果缓存大小超过限制，删除最旧的文件
        total_size = sum(os.path.getsize(os.path.join(self.cache_dir, f))
                        for f in os.listdir(self.cache_dir)
                        if os.path.isfile(os.path.join(self.cache_dir, f)))

        if total_size > self.max_size:
            files = [(os.path.join(self.cache_dir, f),
                     os.path.getsize(os.path.join(self.cache_dir, f)),
                     os.path.getmtime(os.path.join(self.cache_dir, f)))
                    for f in os.listdir(self.cache_dir)
                    if os.path.isfile(os.path.join(self.cache_dir, f))]

            # 按文件大小降序排序，优先删除大文件
            files.sort(key=lambda x: (-x[1], x[2]))

            # 从最大的文件开始删除，直到缓存大小小于限制
            for file_path, file_size, _ in files[:-1]:  # 保留最新的文件
                if total_size <= self.max_size:
                    break
                os.remove(file_path)
                total_size -= file_size 