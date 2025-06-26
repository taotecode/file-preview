import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  build: {
    outDir: '../dist',
    emptyOutDir: true,
    sourcemap: false,
    // 生成静态资源的存放路径
    assetsDir: 'assets',
    // 小于此阈值的导入或引用资源将内联为 base64 编码
    assetsInlineLimit: 4096
  },
  server: {
    port: 5173, // 明确设置开发服务器端口
    strictPort: true, // 如果端口被占用，则会直接退出
    host: '0.0.0.0', // 允许从任何IP访问
    cors: true, // 启用CORS
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true
      }
    },
    fs: {
      // 允许使用任何URL参数，解决链接包含外部URL的问题
      allow: ['..'],
      strict: false
    }
  }
}) 