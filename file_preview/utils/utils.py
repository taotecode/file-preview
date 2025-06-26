"""
通用工具函数
"""

import hashlib

def get_string_md5(text):
    """
    计算字符串的MD5值
    
    Args:
        text: 要计算MD5的字符串
        
    Returns:
        字符串的MD5哈希值
    """
    if isinstance(text, str):
        text = text.encode('utf-8')
    return hashlib.md5(text).hexdigest() 