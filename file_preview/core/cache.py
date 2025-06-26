"""
缓存管理器
"""

import os
import hashlib
import shutil
import time
import json
import logging
from typing import Optional, Dict, Any, List, Union, Tuple
from datetime import datetime, timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger('file_preview')

class BaseCacheBackend:
    """缓存后端基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化缓存后端"""
        self.config = config
    
    def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        raise NotImplementedError
    
    def set(self, key: str, value: str, expire: int = None) -> bool:
        """设置缓存值"""
        raise NotImplementedError
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        raise NotImplementedError
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        raise NotImplementedError
    
    def keys(self, pattern: str) -> List[str]:
        """获取匹配的缓存键列表"""
        raise NotImplementedError
    
    def get_many(self, keys: List[str]) -> Dict[str, str]:
        """批量获取缓存值"""
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    def set_many(self, mapping: Dict[str, str], expire: int = None) -> bool:
        """批量设置缓存值"""
        success = True
        for key, value in mapping.items():
            if not self.set(key, value, expire):
                success = False
        return success
    
    def delete_many(self, keys: List[str]) -> int:
        """批量删除缓存值"""
        count = 0
        for key in keys:
            if self.delete(key):
                count += 1
        return count
    
    def clear(self) -> bool:
        """清空缓存"""
        raise NotImplementedError
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        raise NotImplementedError

class FileCacheBackend(BaseCacheBackend):
    """文件缓存后端"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化文件缓存后端"""
        super().__init__(config)
        self.cache_dir = config['directories']['cache']
        self.max_size = config.get('cache', {}).get('max_size', 1024) * 1024 * 1024  # 默认1GB，转换为字节
        self.retention_days = config.get('cache', {}).get('retention_days', 7)
        
        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 清理过期缓存
        self.cleanup()
    
    def _get_file_path(self, key: str) -> str:
        """获取缓存文件路径"""
        # 使用hash算法打散目录，避免单目录文件过多
        hash_dir = key[:2]
        dir_path = os.path.join(self.cache_dir, hash_dir)
        os.makedirs(dir_path, exist_ok=True)
        return os.path.join(dir_path, key)
    
    def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        file_path = self._get_file_path(key)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"读取缓存文件失败: {str(e)}")
                return None
        return None
    
    def set(self, key: str, value: str, expire: int = None) -> bool:
        """设置缓存值"""
        file_path = self._get_file_path(key)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(value)
            
            # 如果设置了过期时间，记录到元数据文件
            if expire is not None:
                meta_file = f"{file_path}.meta"
                expire_time = time.time() + expire
                with open(meta_file, 'w', encoding='utf-8') as f:
                    json.dump({"expire": expire_time}, f)
            
            return True
        except Exception as e:
            logger.error(f"写入缓存文件失败: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        file_path = self._get_file_path(key)
        meta_file = f"{file_path}.meta"
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(meta_file):
                os.remove(meta_file)
            return True
        except Exception as e:
            logger.error(f"删除缓存文件失败: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        file_path = self._get_file_path(key)
        if os.path.exists(file_path):
            # 检查是否过期
            meta_file = f"{file_path}.meta"
            if os.path.exists(meta_file):
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                    if 'expire' in meta and time.time() > meta['expire']:
                        # 已过期，删除缓存
                        self.delete(key)
                        return False
                except Exception:
                    pass
            return True
        return False
    
    def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配的缓存键列表"""
        result = []
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                if not file.endswith('.meta'):  # 排除元数据文件
                    # 提取键
                    key = os.path.join(os.path.basename(root), file)
                    if pattern == "*" or pattern in key:
                        result.append(key)
        return result
    
    def clear(self) -> bool:
        """清空缓存"""
        try:
            for item in os.listdir(self.cache_dir):
                item_path = os.path.join(self.cache_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            return True
        except Exception as e:
            logger.error(f"清空缓存失败: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_size = 0
        total_files = 0
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                if not file.endswith('.meta'):  # 排除元数据文件
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                    total_files += 1
        
        return {
            "total_size": total_size,
            "total_files": total_files,
            "max_size": self.max_size,
            "retention_days": self.retention_days,
            "type": "file"
        }
    
    def cleanup(self):
        """
        清理缓存目录
        - 删除过期文件
        - 如果缓存大小超过限制，删除最旧的文件直到缓存大小小于限制
        """
        # 删除过期文件
        now = time.time()
        expired_files = []
        
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                # 检查元数据文件
                if file.endswith('.meta'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            meta = json.load(f)
                        if 'expire' in meta and now > meta['expire']:
                            # 删除主文件和元数据文件
                            main_file = file_path[:-5]  # 去掉.meta后缀
                            if os.path.exists(main_file):
                                expired_files.append((main_file, os.path.getmtime(main_file)))
                                os.remove(main_file)
                            os.remove(file_path)
                    except Exception:
                        pass
                elif not os.path.exists(f"{file_path}.meta"):
                    # 没有元数据文件的情况，检查文件修改时间
                    if now - os.path.getmtime(file_path) > self.retention_days * 24 * 3600:
                        expired_files.append((file_path, os.path.getmtime(file_path)))
                        os.remove(file_path)

        # 如果缓存大小超过限制，删除最旧的文件
        total_size = sum(os.path.getsize(os.path.join(root, file))
                        for root, dirs, files in os.walk(self.cache_dir)
                        for file in files if not file.endswith('.meta'))

        if total_size > self.max_size:
            files = []
            for root, dirs, files_in_dir in os.walk(self.cache_dir):
                for file in files_in_dir:
                    if not file.endswith('.meta'):
                        file_path = os.path.join(root, file)
                        files.append((file_path, 
                                     os.path.getsize(file_path),
                                     os.path.getmtime(file_path)))

            # 按访问时间升序排序，优先删除最旧的文件
            files.sort(key=lambda x: x[2])

            # 从最旧的文件开始删除，直到缓存大小小于限制
            for file_path, file_size, _ in files:
                if total_size <= self.max_size:
                    break
                if os.path.exists(file_path):
                    meta_file = f"{file_path}.meta"
                    if os.path.exists(meta_file):
                        os.remove(meta_file)
                    os.remove(file_path)
                    total_size -= file_size
                    logger.debug(f"删除缓存文件: {file_path}, 大小: {file_size}")

class RedisCacheBackend(BaseCacheBackend):
    """Redis缓存后端"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化Redis缓存后端"""
        super().__init__(config)
        if not REDIS_AVAILABLE:
            raise ImportError("未安装redis模块，无法使用Redis缓存")
        
        redis_config = config.get('redis', {})
        self.prefix = redis_config.get('prefix', 'file_preview:')
        self.client = redis.Redis(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            db=redis_config.get('db', 0),
            password=redis_config.get('password'),
            decode_responses=True
        )
    
    def _add_prefix(self, key: str) -> str:
        """添加键前缀"""
        return f"{self.prefix}{key}"
    
    def _remove_prefix(self, key: str) -> str:
        """移除键前缀"""
        if key.startswith(self.prefix):
            return key[len(self.prefix):]
        return key
    
    def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        try:
            return self.client.get(self._add_prefix(key))
        except Exception as e:
            logger.error(f"Redis获取缓存失败: {str(e)}")
            return None
    
    def set(self, key: str, value: str, expire: int = None) -> bool:
        """设置缓存值"""
        try:
            return self.client.set(self._add_prefix(key), value, ex=expire)
        except Exception as e:
            logger.error(f"Redis设置缓存失败: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            return bool(self.client.delete(self._add_prefix(key)))
        except Exception as e:
            logger.error(f"Redis删除缓存失败: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            return bool(self.client.exists(self._add_prefix(key)))
        except Exception as e:
            logger.error(f"Redis检查缓存存在失败: {str(e)}")
            return False
    
    def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配的缓存键列表"""
        try:
            keys = self.client.keys(self._add_prefix(pattern))
            return [self._remove_prefix(key) for key in keys]
        except Exception as e:
            logger.error(f"Redis获取缓存键失败: {str(e)}")
            return []
    
    def get_many(self, keys: List[str]) -> Dict[str, str]:
        """批量获取缓存值"""
        try:
            prefixed_keys = [self._add_prefix(key) for key in keys]
            values = self.client.mget(prefixed_keys)
            return {key: value for key, value in zip(keys, values) if value is not None}
        except Exception as e:
            logger.error(f"Redis批量获取缓存失败: {str(e)}")
            return super().get_many(keys)
    
    def set_many(self, mapping: Dict[str, str], expire: int = None) -> bool:
        """批量设置缓存值"""
        try:
            pipe = self.client.pipeline()
            for key, value in mapping.items():
                pipe.set(self._add_prefix(key), value, ex=expire)
            pipe.execute()
            return True
        except Exception as e:
            logger.error(f"Redis批量设置缓存失败: {str(e)}")
            return super().set_many(mapping, expire)
    
    def delete_many(self, keys: List[str]) -> int:
        """批量删除缓存值"""
        try:
            prefixed_keys = [self._add_prefix(key) for key in keys]
            return self.client.delete(*prefixed_keys)
        except Exception as e:
            logger.error(f"Redis批量删除缓存失败: {str(e)}")
            return super().delete_many(keys)
    
    def clear(self) -> bool:
        """清空缓存"""
        try:
            keys = self.client.keys(self._add_prefix("*"))
            if keys:
                self.client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Redis清空缓存失败: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            info = self.client.info()
            return {
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", ""),
                "connected_clients": info.get("connected_clients", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
                "total_keys": len(self.keys("*")),
                "type": "redis"
            }
        except Exception as e:
            logger.error(f"Redis获取统计信息失败: {str(e)}")
            return {"type": "redis", "error": str(e)}

class CacheManager:
    """
    缓存管理器，支持本地文件缓存和Redis缓存
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化缓存管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.cache_dir = config['directories']['cache']
        self.use_redis = config.get('redis', {}).get('enabled', False)
        
        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 创建缓存后端
        if self.use_redis and REDIS_AVAILABLE:
            try:
                self.backend = RedisCacheBackend(config)
                logger.info("使用Redis缓存后端")
            except Exception as e:
                logger.warning(f"初始化Redis缓存后端失败: {str(e)}，回退到文件缓存")
                self.backend = FileCacheBackend(config)
        else:
            self.backend = FileCacheBackend(config)
            logger.info("使用文件缓存后端")
    
    def get_file_cache_key(self, file_path: str) -> str:
        """
        生成文件缓存键
        
        Args:
            file_path: 文件路径
            
        Returns:
            缓存键
        """
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return f"file:{file_hash}"
    
    def get_file_info_key(self, file_id: str) -> str:
        """
        生成文件信息缓存键
        
        Args:
            file_id: 文件ID
            
        Returns:
            缓存键
        """
        return f"file_info:{file_id}"
    
    def get_md5_key(self, md5_hash: str) -> str:
        """
        生成MD5映射缓存键
        
        Args:
            md5_hash: 文件MD5哈希值
            
        Returns:
            缓存键
        """
        return f"md5:{md5_hash}"
    
    def get_id_key(self, file_id: str) -> str:
        """
        生成ID映射缓存键
        
        Args:
            file_id: 文件ID
            
        Returns:
            缓存键
        """
        return f"id:{file_id}"
    
    def get_url_mapping_key(self, url_hash: str) -> str:
        """
        生成URL映射缓存键
        
        Args:
            url_hash: URL的哈希值
            
        Returns:
            缓存键
        """
        return f"url_mapping:{url_hash}"
    
    def get_cache_path(self, cache_key: str) -> str:
        """
        获取缓存文件路径
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存文件路径
        """
        # 创建层级目录结构
        key_parts = cache_key.split(':')
        if len(key_parts) >= 2:
            # 使用缓存键的前缀和前两个字符作为目录结构
            prefix = key_parts[0]
            hash_start = key_parts[1][:2] if len(key_parts[1]) > 2 else key_parts[1]
            dir_path = os.path.join(self.cache_dir, prefix, hash_start)
            os.makedirs(dir_path, exist_ok=True)
            return os.path.join(dir_path, f"{cache_key.replace(':', '_')}.cache")
        else:
            # 简单结构
            os.makedirs(self.cache_dir, exist_ok=True)
            return os.path.join(self.cache_dir, f"{cache_key.replace(':', '_')}.cache")
    
    def exists(self, file_path: str) -> bool:
        """
        检查文件是否已缓存
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否已缓存
        """
        cache_key = self.get_file_cache_key(file_path)
        return self.backend.exists(cache_key)
    
    def get(self, key: str) -> Optional[str]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在则返回 None
        """
        # 检查是否为特殊键（如URL映射），这些键不应该被当作文件路径处理
        if key.startswith('url_mapping:') or key.startswith('md5:') or key.startswith('id:') or key.startswith('file_info:'):
            return self.backend.get(key)
        
        # 对于文件路径，使用原有的处理方式
        try:
            cache_key = self.get_file_cache_key(key)
            
            # 文件类型的缓存特殊处理
            if isinstance(self.backend, FileCacheBackend):
                if self.backend.exists(cache_key):
                    return self.get_cache_path(cache_key)
                return None
            
            # Redis类型，获取存储的文件路径
            cached_path = self.backend.get(cache_key)
            return cached_path if cached_path and os.path.exists(cached_path) else None
        except FileNotFoundError:
            logger.error(f"尝试访问不存在的文件: {key}")
            return None
    
    def put(self, source_path: str, target_path: str) -> str:
        """
        将文件添加到缓存
        
        Args:
            source_path: 源文件路径
            target_path: 目标文件路径（例如PDF文件）
            
        Returns:
            缓存文件路径
        """
        # 生成缓存键
        cache_key = self.get_file_cache_key(source_path)
        cache_path = self.get_cache_path(cache_key)

        # 如果缓存文件不存在，复制文件到缓存
        if not os.path.exists(cache_path):
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            shutil.copy2(target_path, cache_path)

        # 将路径存储到缓存后端
        self.backend.set(cache_key, cache_path)

        return cache_path
    
    def put_file_info(self, file_id: str, file_info: Dict[str, Any], expire: int = None) -> bool:
        """
        缓存文件信息
        
        Args:
            file_id: 文件ID
            file_info: 文件信息字典
            expire: 过期时间（秒）
            
        Returns:
            是否成功
        """
        cache_key = self.get_file_info_key(file_id)
        return self.backend.set(cache_key, json.dumps(file_info), expire)
    
    def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        
        Args:
            file_id: 文件ID
            
        Returns:
            文件信息字典，如果不存在则返回None
        """
        cache_key = self.get_file_info_key(file_id)
        data = self.backend.get(cache_key)
        if data:
            try:
                return json.loads(data)
            except Exception as e:
                logger.error(f"解析文件信息失败: {str(e)}")
        return None
    
    def put_md5_mapping(self, md5_hash: str, file_id: str, expire: int = None) -> bool:
        """
        添加MD5到文件ID的映射
        
        Args:
            md5_hash: 文件MD5哈希值
            file_id: 文件ID
            expire: 过期时间（秒）
            
        Returns:
            是否成功
        """
        cache_key = self.get_md5_key(md5_hash)
        return self.backend.set(cache_key, file_id, expire)
    
    def get_file_id_by_md5(self, md5_hash: str) -> Optional[str]:
        """
        通过MD5获取文件ID
        
        Args:
            md5_hash: 文件MD5哈希值
            
        Returns:
            文件ID，如果不存在则返回None
        """
        cache_key = self.get_md5_key(md5_hash)
        return self.backend.get(cache_key)
    
    def put_id_mapping(self, file_id: str, file_path: str, expire: int = None) -> bool:
        """
        添加文件ID到文件路径的映射
        
        Args:
            file_id: 文件ID
            file_path: 文件路径
            expire: 过期时间（秒）
            
        Returns:
            是否成功
        """
        cache_key = self.get_id_key(file_id)
        return self.backend.set(cache_key, file_path, expire)
    
    def get_file_path_by_id(self, file_id: str) -> Optional[str]:
        """
        通过文件ID获取文件路径
        
        Args:
            file_id: 文件ID
            
        Returns:
            文件路径，如果不存在则返回None
        """
        cache_key = self.get_id_key(file_id)
        return self.backend.get(cache_key)
    
    def delete_file_info(self, file_id: str) -> bool:
        """
        删除文件信息
        
        Args:
            file_id: 文件ID
            
        Returns:
            是否成功
        """
        cache_key = self.get_file_info_key(file_id)
        return self.backend.delete(cache_key)
    
    def delete_md5_mapping(self, md5_hash: str) -> bool:
        """
        删除MD5映射
        
        Args:
            md5_hash: 文件MD5哈希值
            
        Returns:
            是否成功
        """
        cache_key = self.get_md5_key(md5_hash)
        return self.backend.delete(cache_key)
    
    def delete_id_mapping(self, file_id: str) -> bool:
        """
        删除ID映射
        
        Args:
            file_id: 文件ID
            
        Returns:
            是否成功
        """
        cache_key = self.get_id_key(file_id)
        return self.backend.delete(cache_key)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        return self.backend.get_stats()
    
    def cleanup(self):
        """
        清理缓存
        """
        if isinstance(self.backend, FileCacheBackend):
            self.backend.cleanup() 