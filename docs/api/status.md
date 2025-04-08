# 系统状态 API

## 获取系统状态

获取系统的运行状态和性能指标。

### 请求

```
GET /api/status
```

### 参数

无

### 请求示例

```bash
curl -X GET http://localhost:5000/api/status
```

### 响应

成功响应：
```json
{
    "status": "running",
    "uptime": 3600,
    "memory_usage": {
        "total": 1024,
        "used": 512,
        "free": 512,
        "percent": 50
    },
    "disk_usage": {
        "total": 10240,
        "used": 5120,
        "free": 5120,
        "percent": 50
    },
    "cache": {
        "total_files": 100,
        "total_size": 1024,
        "oldest_file": "2024-04-01T00:00:00Z",
        "newest_file": "2024-04-08T00:00:00Z"
    },
    "conversion": {
        "total_conversions": 1000,
        "successful_conversions": 950,
        "failed_conversions": 50,
        "average_time": 5.5
    }
}
```

错误响应：
```json
{
    "error": "无法获取系统状态"
}
```

## 获取缓存信息

获取缓存的使用情况和统计信息。

### 请求

```
GET /api/status/cache
```

### 参数

无

### 请求示例

```bash
curl -X GET http://localhost:5000/api/status/cache
```

### 响应

成功响应：
```json
{
    "total_files": 100,
    "total_size": 1024,
    "oldest_file": "2024-04-01T00:00:00Z",
    "newest_file": "2024-04-08T00:00:00Z",
    "files_by_type": {
        "docx": 50,
        "xlsx": 30,
        "txt": 20
    },
    "size_by_type": {
        "docx": 512,
        "xlsx": 256,
        "txt": 256
    }
}
```

错误响应：
```json
{
    "error": "无法获取缓存信息"
}
```

## 注意事项

1. 系统状态 API 需要管理员权限
2. 缓存信息每 5 分钟更新一次
3. 性能指标每 1 分钟更新一次
4. 历史数据保留 30 天

## 错误码

| 错误码 | 描述 |
|--------|------|
| 401 | 未授权 |
| 403 | 禁止访问 |
| 500 | 服务器内部错误 |

## 示例代码

### Python

```python
import requests
from datetime import datetime

# 获取系统状态
response = requests.get('http://localhost:5000/api/status')
data = response.json()

if 'error' not in data:
    print(f"系统状态: {data['status']}")
    print(f"运行时间: {data['uptime']} 秒")
    print(f"内存使用: {data['memory_usage']['percent']}%")
    print(f"磁盘使用: {data['disk_usage']['percent']}%")
    print(f"缓存文件数: {data['cache']['total_files']}")
    print(f"总转换次数: {data['conversion']['total_conversions']}")
else:
    print(f"错误: {data['error']}")

# 获取缓存信息
response = requests.get('http://localhost:5000/api/status/cache')
data = response.json()

if 'error' not in data:
    print(f"缓存文件总数: {data['total_files']}")
    print(f"缓存总大小: {data['total_size']} MB")
    print(f"最早文件: {data['oldest_file']}")
    print(f"最新文件: {data['newest_file']}")
    print("文件类型分布:")
    for file_type, count in data['files_by_type'].items():
        print(f"  {file_type}: {count}")
else:
    print(f"错误: {data['error']}")
```

### JavaScript

```javascript
// 获取系统状态
fetch('http://localhost:5000/api/status')
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      console.error(`错误: ${data.error}`);
      return;
    }
    
    console.log(`系统状态: ${data.status}`);
    console.log(`运行时间: ${data.uptime} 秒`);
    console.log(`内存使用: ${data.memory_usage.percent}%`);
    console.log(`磁盘使用: ${data.disk_usage.percent}%`);
    console.log(`缓存文件数: ${data.cache.total_files}`);
    console.log(`总转换次数: ${data.conversion.total_conversions}`);
  });

// 获取缓存信息
fetch('http://localhost:5000/api/status/cache')
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      console.error(`错误: ${data.error}`);
      return;
    }
    
    console.log(`缓存文件总数: ${data.total_files}`);
    console.log(`缓存总大小: ${data.total_size} MB`);
    console.log(`最早文件: ${data.oldest_file}`);
    console.log(`最新文件: ${data.newest_file}`);
    console.log('文件类型分布:');
    Object.entries(data.files_by_type).forEach(([type, count]) => {
      console.log(`  ${type}: ${count}`);
    });
  });
```

## 监控建议

1. 定期检查系统状态
2. 设置内存和磁盘使用阈值
3. 监控转换成功率
4. 定期清理缓存
5. 记录性能指标 