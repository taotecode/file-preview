# 文件预览系统开发者指南

## 1. 系统架构

文件预览系统采用前后端分离的架构设计，主要由以下几个部分组成：

### 1.1 整体架构图

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   前端应用   │ <--> │   后端API   │ <--> │ 文件转换服务 │
└─────────────┘      └─────────────┘      └─────────────┘
                           ^                     ^
                           |                     |
                           v                     v
                     ┌─────────────┐      ┌─────────────┐
                     │  文件存储   │      │ 任务队列系统 │
                     └─────────────┘      └─────────────┘
```

### 1.2 核心组件

#### 1.2.1 前端应用

- **技术栈**：Vue.js 3, TypeScript, Tailwind CSS
- **主要功能**：用户界面交互，文件上传，预览展示
- **目录结构**：`frontend/`目录下

#### 1.2.2 后端API服务

- **技术栈**：Python, Flask
- **主要功能**：接收前端请求，管理文件元数据，协调转换任务
- **目录结构**：`server/`目录下

#### 1.2.3 文件转换服务

- **技术栈**：Python, 多种转换库和工具
- **主要功能**：将上传的文件转换为可预览的格式
- **目录结构**：`converter/`目录下

#### 1.2.4 文件存储

- **实现方式**：本地文件系统或云存储(可配置)
- **目录结构**：`tmp/file_preview/`目录下

#### 1.2.5 任务队列系统

- **技术栈**：Redis, Celery(可选)
- **主要功能**：异步处理文件转换任务
- **实现位置**：`utils/tasks.py`

## 2. 开发环境搭建

### 2.1 系统要求

- Python 3.8+
- Node.js 14+
- Redis (用于任务队列)
- 相关依赖库和工具(LibreOffice, ImageMagick等)

### 2.2 开发环境准备

#### 2.2.1 克隆代码库

```bash
git clone https://github.com/yourusername/file_previews.git
cd file_previews
```

#### 2.2.2 后端环境配置

```bash
# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装转换工具依赖(以Ubuntu为例)
sudo apt-get update
sudo apt-get install -y libreoffice imagemagick poppler-utils
```

#### 2.2.3 前端环境配置

```bash
cd frontend
npm install
```

### 2.3 配置文件

系统配置文件位于`config.yaml`，开发者可根据需要修改配置:

```yaml
server:
  host: 0.0.0.0
  port: 5001
  debug: true

paths:
  download_dir: tmp/file_preview/download
  convert_dir: tmp/file_preview/convert
  cache_dir: tmp/file_preview/cache
  log_dir: tmp/file_preview/log

converter:
  timeout: 60
  max_retries: 3
  
# 更多配置...
```

### 2.4 启动开发服务

```bash
# 启动后端服务
python app.py

# 在另一个终端窗口启动前端开发服务
cd frontend
npm run dev
```

## 3. 代码结构

### 3.1 目录结构概览

```
file_previews/
├── app.py                # 应用入口文件
├── config.yaml           # 配置文件
├── server/               # 后端服务
│   ├── __init__.py
│   ├── api/              # API模块
│   │   ├── __init__.py
│   │   ├── converter.py  # 转换API
│   │   ├── files.py      # 文件操作API
│   │   └── ...
│   ├── routes/           # 路由定义
│   │   ├── __init__.py
│   │   ├── api.py
│   │   └── views.py
│   └── views/            # 视图函数
│       ├── __init__.py
│       └── preview.py
├── converter/            # 文件转换模块
│   ├── __init__.py
│   ├── handlers/         # 各种文件类型处理器
│   │   ├── __init__.py
│   │   ├── document.py
│   │   ├── image.py
│   │   └── ...
│   └── converter.py      # 转换器主类
├── utils/                # 工具函数
│   ├── __init__.py
│   ├── file_utils.py
│   ├── tasks.py          # 任务处理
│   └── ...
├── frontend/             # 前端应用
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── components/   # 组件
│   │   ├── views/        # 页面
│   │   ├── services/     # API服务
│   │   └── ...
│   └── ...
└── tests/                # 测试代码
    ├── test_server.py
    ├── test_converter.py
    └── ...
```

## 4. 开发指南

### 4.1 后端开发

#### 4.1.1 添加新的API端点

1. 在`server/api/`目录下创建或修改现有API文件
2. 定义API函数，例如:

```python
# server/api/example.py
from flask import jsonify, request, current_app

def example_endpoint():
    """示例API端点"""
    # 获取请求参数
    param = request.args.get('param', '')
    
    # 处理业务逻辑
    result = {"status": "success", "data": param}
    
    # 返回JSON响应
    return jsonify(result)
```

3. 在`server/routes/api.py`中注册API路由:

```python
# server/routes/api.py
from server.api import example

# 注册路由
@api_bp.route('/example', methods=['GET'])
def example_route():
    return example.example_endpoint()
```

#### 4.1.2 添加新的文件转换处理器

1. 在`converter/handlers/`目录下创建新的处理器文件
2. 实现处理器类，例如:

```python
# converter/handlers/new_format.py
from converter.handlers.base import BaseHandler

class NewFormatHandler(BaseHandler):
    """新格式文件处理器"""
    
    def __init__(self):
        super().__init__()
        self.supported_formats = ['.xyz']
    
    def can_handle(self, file_path):
        """检查是否能处理该文件"""
        ext = self._get_extension(file_path)
        return ext.lower() in self.supported_formats
    
    def convert(self, file_path, output_dir):
        """转换文件为可预览格式"""
        # 实现转换逻辑
        output_path = os.path.join(output_dir, f"{os.path.basename(file_path)}.pdf")
        
        # 转换代码...
        
        return output_path if os.path.exists(output_path) else None
```

3. 在`converter/handlers/__init__.py`中注册新处理器:

```python
# converter/handlers/__init__.py
from converter.handlers.new_format import NewFormatHandler

def get_all_handlers():
    """获取所有处理器实例"""
    handlers = [
        # 其他已有处理器...
        NewFormatHandler(),
    ]
    return handlers
```

### 4.2 前端开发

#### 4.2.1 添加新组件

1. 在`frontend/src/components/`目录下创建新组件:

```vue
<!-- frontend/src/components/ExampleComponent.vue -->
<template>
  <div class="example-component">
    <h2>{{ title }}</h2>
    <p>{{ message }}</p>
    <button @click="handleClick">点击我</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface Props {
  title: string;
  message?: string;
}

const props = withDefaults(defineProps<Props>(), {
  message: '默认消息'
});

const emit = defineEmits<{
  (e: 'click', value: string): void
}>();

const handleClick = () => {
  emit('click', props.title);
};
</script>

<style scoped>
.example-component {
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 0.5rem;
}
</style>
```

2. 在页面中使用新组件:

```vue
<!-- frontend/src/views/SomePage.vue -->
<template>
  <div class="some-page">
    <ExampleComponent 
      title="示例组件" 
      message="这是一个新组件" 
      @click="handleComponentClick" 
    />
  </div>
</template>

<script setup lang="ts">
import ExampleComponent from '../components/ExampleComponent.vue';

const handleComponentClick = (value: string) => {
  console.log(`组件点击事件: ${value}`);
};
</script>
```

#### 4.2.2 添加新API服务

1. 在`frontend/src/services/`目录下创建或修改API服务:

```typescript
// frontend/src/services/exampleService.ts
import { apiClient } from './apiClient';

export interface ExampleData {
  id: string;
  name: string;
}

export const exampleService = {
  /**
   * 获取示例数据
   */
  async getExample(): Promise<ExampleData[]> {
    const response = await apiClient.get('/api/example');
    return response.data;
  },
  
  /**
   * 创建示例数据
   */
  async createExample(data: Partial<ExampleData>): Promise<ExampleData> {
    const response = await apiClient.post('/api/example', data);
    return response.data;
  }
};
```

2. 在组件中使用API服务:

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { exampleService, type ExampleData } from '../services/exampleService';

const examples = ref<ExampleData[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);

onMounted(async () => {
  try {
    loading.value = true;
    examples.value = await exampleService.getExample();
  } catch (err) {
    error.value = '获取数据失败';
    console.error(err);
  } finally {
    loading.value = false;
  }
});
</script>
```

## 5. 测试指南

### 5.1 自动化测试

系统使用pytest进行自动化测试，测试代码位于`tests/`目录。

#### 5.1.1 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_server.py

# 运行特定测试类或方法
python -m pytest tests/test_server.py::TestServer
python -m pytest tests/test_server.py::TestServer::test_file_upload
```

#### 5.1.2 编写测试

新的测试应遵循现有的测试结构:

```python
# tests/test_example.py
import pytest
from server import create_app

class TestExample:
    """示例功能测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app = create_app('testing')
        with app.test_client() as client:
            yield client
    
    def test_example_endpoint(self, client):
        """测试示例API端点"""
        # 准备测试数据
        test_param = "test_value"
        
        # 发送请求
        response = client.get(f'/api/example?param={test_param}')
        
        # 断言结果
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data'] == test_param
```

### 5.2 手动测试

除自动化测试外，开发者还应进行以下手动测试:

1. **文件上传测试**：上传各种类型的文件，确保系统正确处理
2. **URL处理测试**：测试通过URL获取文件功能
3. **预览功能测试**：检查不同类型文件的预览效果
4. **边界情况测试**：大文件、空文件、损坏文件等

## 6. 部署指南

### 6.1 生产环境配置

1. 修改`config.yaml`设置生产环境参数:

```yaml
server:
  host: 0.0.0.0
  port: 5001
  debug: false

paths:
  download_dir: /var/lib/file_preview/download
  convert_dir: /var/lib/file_preview/convert
  cache_dir: /var/lib/file_preview/cache
  log_dir: /var/lib/file_preview/log

# 更多生产环境配置...
```

2. 设置环境变量:

```bash
export FLASK_ENV=production
export FLASK_APP=app.py
```

### 6.2 构建前端

```bash
cd frontend
npm run build
```

### 6.3 部署方式

#### 6.3.1 使用Gunicorn和Nginx部署

1. 安装Gunicorn:

```bash
pip install gunicorn
```

2. 启动Gunicorn服务:

```bash
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

3. Nginx配置示例:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /path/to/file_previews/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

#### 6.3.2 使用Docker部署

1. 创建Dockerfile:

```dockerfile
FROM python:3.9-slim

# 安装依赖
RUN apt-get update && apt-get install -y \
    libreoffice \
    imagemagick \
    poppler-utils \
    redis-server \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV FLASK_ENV=production
ENV FLASK_APP=app.py

# 暴露端口
EXPOSE 5001

# 启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
```

2. 创建docker-compose.yml:

```yaml
version: '3'

services:
  web:
    build: .
    ports:
      - "5001:5001"
    volumes:
      - ./tmp:/app/tmp
    depends_on:
      - redis
    environment:
      - FLASK_ENV=production
      - REDIS_URL=redis://redis:6379/0

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
```

3. 启动服务:

```bash
docker-compose up -d
```

## 7. 扩展开发

### 7.1 支持新的文件类型

要添加对新文件类型的支持，需要:

1. 在`converter/handlers/`目录下创建新的处理器
2. 实现文件识别和转换逻辑
3. 更新前端展示部分以支持新类型的预览

### 7.2 添加新功能

添加新功能的一般步骤:

1. 根据架构设计，确定功能应添加在哪个组件
2. 实现后端API和处理逻辑
3. 在前端添加界面和交互
4. 编写测试确保功能正常工作

### 7.3 插件系统开发

为提高扩展性，可以考虑实现插件系统:

1. 定义插件接口和生命周期
2. 实现插件加载和管理机制
3. 在关键点添加钩子以允许插件介入

## 8. 故障排除

### 8.1 常见开发问题

1. **依赖问题**: 确保安装了所有必要的库和工具
2. **路径问题**: 检查配置文件中的路径设置是否正确
3. **权限问题**: 确保程序有足够权限读写文件

### 8.2 调试技巧

1. 启用DEBUG模式获取详细错误信息:
   ```python
   app.config['DEBUG'] = True
   ```

2. 使用日志记录关键信息:
   ```python
   import logging
   logging.info("处理文件: %s", file_path)
   ```

3. 使用断点进行调试:
   ```python
   import pdb; pdb.set_trace()
   ```

## 9. 贡献指南

### 9.1 提交代码

1. 创建功能分支:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. 提交代码:
   ```bash
   git add .
   git commit -m "feat: 添加新功能xxx"
   ```

3. 创建Pull Request请求合并

### 9.2 代码规范

- 遵循PEP 8 Python代码风格
- 使用类型注解提高代码可读性
- 编写清晰的注释和文档字符串
- 编写单元测试涵盖新功能

### 9.3 文档更新

当添加新功能或修改现有功能时，确保同时更新相关文档:

1. API文档 (`docs/guide/api.md`)
2. 用户指南 (`docs/guide/user.md`)
3. 开发者指南 (`docs/guide/developer.md`)

## 10. 参考资源

- [Flask文档](https://flask.palletsprojects.com/)
- [Vue.js文档](https://vuejs.org/)
- [Python官方文档](https://docs.python.org/)
- [主要依赖库文档链接...] 