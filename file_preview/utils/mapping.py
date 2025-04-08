"""
文件映射工具
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger('file_preview')

class FileMapping:
    """
    文件映射类
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.mapping_file = os.path.join(config['directories']['cache'], 'file_mappings.json')
        self.mappings = {}
        self.load()
    
    def load(self) -> None:
        """
        加载映射
        """
        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    self.mappings = json.load(f)
                logger.info(f"已加载 {len(self.mappings)} 个文件映射")
            except Exception as e:
                logger.error(f"加载文件映射失败: {str(e)}", exc_info=True)
                self.mappings = {}
    
    def save(self) -> None:
        """
        保存映射
        """
        try:
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.mappings, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存 {len(self.mappings)} 个文件映射")
        except Exception as e:
            logger.error(f"保存文件映射失败: {str(e)}", exc_info=True)
    
    def get(self, md5_hash: str) -> Optional[str]:
        """
        获取映射的文件路径
        
        Args:
            md5_hash: 文件的 MD5 值
            
        Returns:
            映射的文件路径，如果不存在则返回 None
        """
        if md5_hash in self.mappings:
            mapping = self.mappings[md5_hash]
            if os.path.exists(mapping['path']):
                return mapping['path']
            else:
                del self.mappings[md5_hash]
                self.save()
        return None
    
    def add(self, md5_hash: str, file_path: str, original_name: Optional[str] = None) -> None:
        """
        添加文件映射
        
        Args:
            md5_hash: 文件的 MD5 值
            file_path: 文件路径
            original_name: 原始文件名
        """
        self.mappings[md5_hash] = {
            'path': file_path,
            'original_name': original_name or os.path.basename(file_path),
            'created_at': time.time(),
            'last_accessed': time.time()
        }
        self.save()
    
    def update_access_time(self, md5_hash: str) -> None:
        """
        更新访问时间
        
        Args:
            md5_hash: 文件的 MD5 值
        """
        if md5_hash in self.mappings:
            self.mappings[md5_hash]['last_accessed'] = time.time()
            self.save()
    
    def get_original_name(self, md5_hash: str) -> Optional[str]:
        """
        获取原始文件名
        
        Args:
            md5_hash: 文件的 MD5 值
            
        Returns:
            原始文件名，如果不存在则返回 None
        """
        if md5_hash in self.mappings:
            return self.mappings[md5_hash]['original_name']
        return None
    
    def cleanup(self, retention_days: int = 7) -> None:
        """
        清理过期的映射
        
        Args:
            retention_days: 保留天数
        """
        now = time.time()
        expired = []
        
        for md5_hash, mapping in self.mappings.items():
            if now - mapping['last_accessed'] > retention_days * 86400:
                expired.append(md5_hash)
                try:
                    if os.path.exists(mapping['path']):
                        os.remove(mapping['path'])
                except Exception as e:
                    logger.error(f"删除文件失败: {mapping['path']}, 错误: {str(e)}")
        
        for md5_hash in expired:
            del self.mappings[md5_hash]
        
        if expired:
            self.save()
            logger.info(f"已清理 {len(expired)} 个过期映射") 