"""
文件映射工具
"""

import os
import json
import logging
import time
import uuid
import base64
import hashlib
from typing import Dict, Any, Optional, Tuple, List, Union
from datetime import datetime

from ..core.cache import CacheManager

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
        self.cache_dir = config.get('directories', {}).get('cache', './cache')
        self.cache_manager = CacheManager(config)
        
        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # URL映射存储的子目录
        self.url_mappings_dir = os.path.join(self.cache_dir, 'url_mappings')
        os.makedirs(self.url_mappings_dir, exist_ok=True)
        
        # MD5映射存储的子目录
        self.md5_mappings_dir = os.path.join(self.cache_dir, 'md5_mappings')
        os.makedirs(self.md5_mappings_dir, exist_ok=True)
        
        # 加载现有映射
        self.mappings = self._load_mappings()
        self.retention_days = config.get('cache', {}).get('retention_days', 7)
    
    def _load_mappings(self):
        """加载现有的文件映射"""
        mappings = {}
        try:
            # 尝试从文件或数据库加载映射
            mappings_path = os.path.join(self.cache_dir, 'mappings.json')
            if os.path.exists(mappings_path):
                with open(mappings_path, 'r', encoding='utf-8') as f:
                    mappings = json.load(f)
        except Exception as e:
            logger.error(f"加载文件映射失败: {str(e)}")
        return mappings
    
    def _save_mappings(self):
        """保存文件映射到文件"""
        try:
            mappings_path = os.path.join(self.cache_dir, 'mappings.json')
            with open(mappings_path, 'w', encoding='utf-8') as f:
                json.dump(self.mappings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存文件映射失败: {str(e)}")
    
    def generate_file_id(self) -> str:
        """
        生成唯一文件ID
        
        Returns:
            文件ID
        """
        # 生成12位的随机ID
        while True:
            # 生成UUID并取前12个字符，转为Base62编码
            raw_id = str(uuid.uuid4().hex)[:12]
            # 使用Base64编码但替换特殊字符，使其URL友好
            file_id = base64.b64encode(raw_id.encode()).decode()
            file_id = file_id.replace('+', '-').replace('/', '_').replace('=', '')[:8]
            
            # 确保ID不重复
            if not self.cache_manager.get_file_info(file_id):
                return file_id
    
    def add(self, md5_hash: str, file_path: str, original_name: Optional[str] = None, 
            source_url: Optional[str] = None, original_file_info: Optional[Dict[str, Any]] = None,
            converted_info: Optional[Dict[str, Any]] = None) -> str:
        """
        添加文件映射
        
        Args:
            md5_hash: 文件的 MD5 值
            file_path: 文件路径
            original_name: 原始文件名
            source_url: 文件来源URL
            original_file_info: 原始文件的详细信息
            converted_info: 转换后的文件信息
            
        Returns:
            文件唯一ID
        """
        # 确保使用绝对路径
        if not os.path.isabs(file_path):
            # 获取项目根目录
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            # 尝试转换为绝对路径
            if os.path.exists(file_path):
                file_path = os.path.abspath(file_path)
            elif os.path.exists(os.path.join(root_dir, file_path.lstrip("./"))):
                file_path = os.path.join(root_dir, file_path.lstrip("./"))
                
        # 检查md5是否已经有映射的文件ID
        existing_file_id = self.cache_manager.get_file_id_by_md5(md5_hash)
        if existing_file_id:
            # 如果文件ID已存在，但文件路径不同，需要更新
            existing_file_path = self.cache_manager.get_file_path_by_id(existing_file_id)
            if existing_file_path and os.path.exists(existing_file_path):
                # 获取现有文件信息
                file_info = self.cache_manager.get_file_info(existing_file_id) or {}
                
                # 更新访问时间
                file_info['last_accessed'] = time.time()
                
                # 如果原始文件名不同且提供了新的名称，更新它
                if original_name and file_info.get('original_name') != original_name:
                    file_info['original_name'] = original_name
                
                # 如果提供了URL且现有信息中没有URL，或URL不同，则更新
                if source_url:
                    if 'source_url' not in file_info or file_info['source_url'] != source_url:
                        file_info['source_url'] = source_url
                        # 添加URL映射
                        self._add_url_mapping(source_url, existing_file_id)
                
                # 如果提供了原始文件信息，更新它
                if original_file_info:
                    file_info['original_file_info'] = original_file_info
                
                # 如果提供了转换信息，更新它
                if converted_info:
                    file_info['converted_info'] = converted_info
                
                # 更新文件信息
                self.cache_manager.put_file_info(existing_file_id, file_info)
                
                return existing_file_id
        
        # 生成新的文件ID
        file_id = self.generate_file_id()
        
        # 获取文件信息
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # 确定文件类型
        file_type = "unknown"
        if file_ext in ['.pdf']:
            file_type = "pdf"
        elif file_ext in ['.doc', '.docx', '.rtf', '.txt']:
            file_type = "document"
        elif file_ext in ['.xls', '.xlsx']:
            file_type = "excel"
        elif file_ext in ['.ppt', '.pptx']:
            file_type = "presentation"
        elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            file_type = "image"
        
        # 创建文件信息字典
        file_info = {
            'file_id': file_id,
            'md5_hash': md5_hash,
            'path': file_path,
            'original_name': original_name or os.path.basename(file_path),
            'file_size': file_size,
            'extension': file_ext,
            'file_type': file_type,
            'creation_time': time.time(),
            'last_accessed': time.time()
        }
        
        # 添加来源URL（如果提供）
        if source_url:
            file_info['source_url'] = source_url
            # 添加URL映射
            self._add_url_mapping(source_url, file_id)
        
        # 添加原始文件信息（如果提供）
        if original_file_info:
            file_info['original_file_info'] = original_file_info
        
        # 添加转换信息（如果提供）
        if converted_info:
            file_info['converted_info'] = converted_info
        
        # 保存文件信息
        self.cache_manager.put_file_info(file_id, file_info)
        
        # 保存MD5映射
        self.cache_manager.put_md5_mapping(md5_hash, file_id)
        
        # 保存文件ID映射
        self.cache_manager.put_id_mapping(file_id, file_path)
        
        logger.info(f"添加文件映射: {md5_hash} -> {file_id} ({file_path})")
        
        return file_id
    
    # 兼容性别名，用于支持旧的 add_file 调用
    def add_file(self, file_path: str, original_name: Optional[str] = None, source_url: Optional[str] = None) -> str:
        """
        添加文件映射（兼容旧的 API 调用）
        
        Args:
            file_path: 文件路径
            original_name: 原始文件名
            source_url: 文件来源URL
            
        Returns:
            文件唯一ID
        """
        # 计算文件的 MD5
        try:
            from .file_utils import get_file_md5
            md5_hash = get_file_md5(file_path)
        except ImportError:
            # 简单实现 MD5 计算
            md5_hash = ""
            with open(file_path, 'rb') as f:
                md5_hash = hashlib.md5(f.read()).hexdigest()
        
        return self.add(md5_hash, file_path, original_name, source_url)
    
    def _add_url_mapping(self, url: str, file_id: str) -> bool:
        """
        添加URL到文件ID的映射
        
        Args:
            url: 文件URL
            file_id: 文件ID
            
        Returns:
            是否成功
        """
        try:
            # 生成URL的键名
            url_key = f"url_mapping:{self._hash_url(url)}"
            
            # 直接使用缓存后端存储
            success = self.cache_manager.backend.set(url_key, file_id)
            
            if success:
                logger.info(f"已添加URL映射: {url} -> {file_id}")
            else:
                logger.error(f"添加URL映射失败: {url} -> {file_id}")
            
            return success
        except Exception as e:
            logger.exception(f"添加URL映射时发生错误: {url} -> {file_id}, 错误: {str(e)}")
            return False
    
    def _hash_url(self, url: str) -> str:
        """
        对URL进行哈希，以便于存储
        
        Args:
            url: 需要哈希的URL
            
        Returns:
            哈希后的字符串
        """
        return hashlib.md5(url.encode()).hexdigest()
    
    def get_id_by_url(self, url: str) -> Optional[str]:
        """
        通过URL获取文件ID
        
        Args:
            url: 文件URL
            
        Returns:
            文件ID，如果不存在则返回None
        """
        url_key = f"url_mapping:{self._hash_url(url)}"
        return self.cache_manager.backend.get(url_key)
    
    def get_by_url(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        通过URL获取文件信息
        
        Args:
            url: 文件URL
            
        Returns:
            (文件路径, 原始文件名)元组，如果不存在则返回(None, None)
        """
        file_id = self.get_id_by_url(url)
        if not file_id:
            return None, None
        
        return self.get_by_id(file_id)
    
    def get_file_info_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        通过URL获取文件详细信息
        
        Args:
            url: 文件URL
            
        Returns:
            文件信息字典，如果不存在则返回None
        """
        file_id = self.get_id_by_url(url)
        if not file_id:
            return None
        
        return self.get_file_info(file_id)
    
    def get(self, md5_hash: str) -> Optional[str]:
        """
        获取映射的文件路径
        
        Args:
            md5_hash: 文件的 MD5 值
            
        Returns:
            映射的文件路径，如果不存在则返回 None
        """
        # 通过MD5获取文件ID
        file_id = self.cache_manager.get_file_id_by_md5(md5_hash)
        if not file_id:
            return None
        
        # 通过文件ID获取文件路径
        file_path = self.cache_manager.get_file_path_by_id(file_id)
        if not file_path or not os.path.exists(file_path):
            # 如果文件不存在，清理无效映射
            self.delete(file_id)
            return None
        
        # 更新最后访问时间
        self.update_access_time(file_id)
        
        return file_path
    
    def get_by_id(self, file_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        通过ID获取文件信息
        
        Args:
            file_id: 文件ID
            
        Returns:
            (文件路径, 原始文件名)元组，如果不存在则返回(None, None)
        """
        # 获取文件信息
        file_info = self.cache_manager.get_file_info(file_id)
        if not file_info:
            return None, None
        
        # 获取文件路径
        file_path = file_info.get('path')
        if not file_path or not os.path.exists(file_path):
            # 清理无效映射
            self.delete(file_id)
            return None, None
        
        # 更新最后访问时间
        self.update_access_time(file_id)
        
        return file_path, file_info.get('original_name')
    
    def update_access_time(self, file_id: str) -> bool:
        """
        更新访问时间
        
        Args:
            file_id: 文件ID
            
        Returns:
            是否成功
        """
        # 获取文件信息
        file_info = self.cache_manager.get_file_info(file_id)
        if not file_info:
            return False
        
        # 更新访问时间
        file_info['last_accessed'] = time.time()
        
        # 更新缓存
        return self.cache_manager.put_file_info(file_id, file_info)
    
    def get_id_by_md5(self, md5_hash: str) -> Optional[str]:
        """
        通过MD5哈希值获取文件ID
        
        Args:
            md5_hash: 文件的MD5值
            
        Returns:
            文件ID，如果不存在则返回None
        """
        return self.cache_manager.get_file_id_by_md5(md5_hash)
    
    def get_original_name(self, md5_hash: str) -> Optional[str]:
        """
        获取原始文件名
        
        Args:
            md5_hash: 文件的 MD5 值
            
        Returns:
            原始文件名，如果不存在则返回 None
        """
        # 通过MD5获取文件ID
        file_id = self.cache_manager.get_file_id_by_md5(md5_hash)
        if not file_id:
            return None
        
        # 获取文件信息
        file_info = self.cache_manager.get_file_info(file_id)
        if not file_info:
            return None
        
        return file_info.get('original_name')
    
    def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        获取文件详细信息
        
        Args:
            file_id: 文件ID
            
        Returns:
            文件信息字典，如果不存在则返回None
        """
        # 获取文件信息
        file_info = self.cache_manager.get_file_info(file_id)
        if not file_info:
            return None
        
        # 更新最后访问时间
        self.update_access_time(file_id)
        
        return file_info
    
    def get_file_info_by_md5(self, md5_hash: str) -> Optional[Dict[str, Any]]:
        """
        通过MD5获取文件详细信息
        
        Args:
            md5_hash: 文件的 MD5 值
            
        Returns:
            文件信息字典，如果不存在则返回None
        """
        # 通过MD5获取文件ID
        file_id = self.cache_manager.get_file_id_by_md5(md5_hash)
        if not file_id:
            return None
        
        return self.get_file_info(file_id)
    
    def get_original_path(self, filename: str) -> Optional[str]:
        """
        通过文件名查找原始文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            原始文件路径，如果不存在则返回 None
        """
        # 查找所有文件信息，寻找匹配的原始文件名
        # 注意：这是一个较为耗时的操作，因为需要遍历所有文件信息
        found_file_id = None
        download_dir = self.config['directories']['download']
        
        # 尝试直接在下载目录查找
        direct_path = os.path.join(download_dir, filename)
        if os.path.exists(direct_path):
            return direct_path

        # 计算文件名的MD5，可能用于快速查找
        filename_md5 = hashlib.md5(filename.encode()).hexdigest()
        
        # 尝试通过文件名的MD5查找
        file_id = self.cache_manager.get_file_id_by_md5(filename_md5)
        if file_id:
            file_info = self.cache_manager.get_file_info(file_id)
            if file_info and file_info.get('original_name') == filename:
                file_path = file_info.get('path')
                if file_path and os.path.exists(file_path):
                    return file_path
        
        # 需要迭代查找所有缓存的文件信息
        # 这里可能需要针对性的优化，例如建立文件名索引
        # 临时方案：使用缓存后端的keys方法查找所有文件信息
        for key in self.cache_manager.backend.keys("file_info:*"):
            if key.startswith("file_info:"):
                try:
                    file_id = key[10:]  # 去掉 "file_info:" 前缀
                    file_info = self.cache_manager.get_file_info(file_id)
                    if file_info and file_info.get('original_name') == filename:
                        found_file_id = file_id
                        break
                except Exception as e:
                    logger.error(f"解析文件信息失败: {str(e)}")
        
        if found_file_id:
            file_info = self.cache_manager.get_file_info(found_file_id)
            file_path = file_info.get('path') if file_info else None
            
            # 检查文件是否存在
            if file_path and os.path.exists(file_path):
                return file_path
        
        return None
    
    def delete(self, file_id: str) -> bool:
        """
        删除文件映射
        
        Args:
            file_id: 文件ID
            
        Returns:
            是否成功
        """
        # 获取文件信息
        file_info = self.cache_manager.get_file_info(file_id)
        if not file_info:
            return False
        
        # 删除MD5映射
        md5_hash = file_info.get('md5_hash')
        if md5_hash:
            self.cache_manager.delete_md5_mapping(md5_hash)
        
        # 删除文件信息
        self.cache_manager.delete_file_info(file_id)
        
        # 删除ID映射
        self.cache_manager.delete_id_mapping(file_id)
        
        logger.info(f"删除文件映射: {file_id}")
        
        return True
    
    def list_files(self, limit: int = 20, offset: int = 0, 
                   filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        获取文件列表
        
        Args:
            limit: 每页记录数
            offset: 偏移量
            filters: 过滤条件，如 {'file_type': 'excel'}
            
        Returns:
            list: 文件信息列表
        """
        # 获取所有的文件ID
        all_file_ids = self.cache_manager.scan_keys("file_info:*")
        all_file_ids = [key.split(':')[1] for key in all_file_ids if ':' in key]
        
        # 使用列表推导式构建结果
        result = []
        for file_id in all_file_ids:
            info = self.get_file_info(file_id)
            if info and self._match_filters(info, filters):
                info['file_id'] = file_id
                result.append(info)
        
        # 按最后访问时间排序（最新的排在前面）
        result.sort(key=lambda x: x.get('last_accessed', 0), reverse=True)
        
        # 应用分页
        paginated_result = result[offset:offset+limit] if offset < len(result) else []
        
        return paginated_result
    
    def _match_filters(self, file_info, filters):
        """
        检查文件信息是否匹配过滤条件
        
        Args:
            file_info: 文件信息
            filters: 过滤条件
            
        Returns:
            bool: 是否匹配
        """
        if not filters:
            return True
            
        for key, value in filters.items():
            if key not in file_info or file_info[key] != value:
                return False
                
        return True
    
    def cleanup(self, retention_days: Optional[int] = None) -> int:
        """
        清理过期的映射
        
        Args:
            retention_days: 保留天数，默认使用配置中的值
            
        Returns:
            清理的记录数
        """
        if retention_days is None:
            retention_days = self.retention_days
        
        now = time.time()
        expired_count = 0
        
        # 获取所有文件信息键
        for key in self.cache_manager.backend.keys("file_info:*"):
            if key.startswith("file_info:"):
                try:
                    file_id = key[10:]  # 去掉 "file_info:" 前缀
                    file_info = self.cache_manager.get_file_info(file_id)
                    
                    # 检查是否过期
                    if file_info and now - file_info.get('last_accessed', 0) > retention_days * 86400:
                        # 删除文件映射
                        if self.delete(file_id):
                            expired_count += 1
                except Exception as e:
                    logger.error(f"清理过期映射失败: {str(e)}")
        
        if expired_count > 0:
            logger.info(f"已清理 {expired_count} 个过期映射")
        
        return expired_count 