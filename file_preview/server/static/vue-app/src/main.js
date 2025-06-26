import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'

// 获取后端传递的参数
const previewParams = window.previewParams || {}

// 定义全局Buffer polyfill
if (typeof window !== 'undefined' && !window.Buffer) {
  window.Buffer = {
    from: (data, encoding) => {
      if (encoding === 'base64') {
        const binary = window.atob(data);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
          bytes[i] = binary.charCodeAt(i);
        }
        return bytes;
      }
      return null;
    }
  };
}

const app = createApp(App, { 
  initialParams: previewParams  // 传递到App组件
})

app.use(ElementPlus)
app.mount('#app') 