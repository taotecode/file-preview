# Excel文件预览前端

这是一个基于Vue 3的Excel文件预览应用，用于在浏览器中直接查看Excel文件，无需将其转换为PDF。

## 环境要求

- Node.js 20.x (推荐使用nvm管理Node.js版本)
- npm 9.x 或更高版本

## 主要功能

- 支持直接预览xlsx和xls文件
- 支持多工作表切换
- 支持将Excel转换为PDF（可选）
- 支持下载原始Excel文件

## 技术栈

- Vue 3 (Composition API)
- Vite
- Element Plus 组件库
- @vue-office/excel 用于预览xlsx文件
- SheetJS (xlsx) 用于解析xls文件
- Tailwind CSS 用于样式

## 安装依赖

```bash
# 切换到Node.js 20.x版本
nvm use 20

# 安装依赖
cd file_preview/server/static/vue-app
npm install
```

## 开发

```bash
# 开发模式
npm run dev

# 构建生产版本
npm run build
```

## 集成到文件预览后端

应用构建后，静态文件会输出到`../dist`目录，Flask服务器会自动提供这些静态文件。

注意：在部署到生产环境时，需要确保已经执行了`npm run build`命令，并且构建后的文件已经正确放置在`../dist`目录中。

## 使用说明

1. 当用户上传或提供Excel文件时，系统默认直接使用Vue前端预览，而不是转换为PDF
2. 用户可以通过预览界面中的"转为PDF"按钮将当前Excel文件转换为PDF格式
3. 预览界面还提供"下载原始文件"选项，方便用户获取原始Excel文件

## 支持的文件格式

- `.xlsx` - 使用@vue-office/excel组件直接预览
- `.xls` - 使用自定义组件基于SheetJS解析后预览 