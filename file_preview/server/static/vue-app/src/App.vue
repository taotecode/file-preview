<template>
  <div class="app-container">
    <component :is="currentComponent" v-if="currentComponent" v-bind="componentProps"></component>
  </div>
</template>

<script setup>
import { ref, onMounted, shallowRef } from 'vue'
import ExcelPreview from './views/ExcelPreview.vue'
import PdfViewer from './views/PdfViewer.vue'

const props = defineProps({
  initialParams: {
    type: Object,
    default: () => ({})
  }
})

const currentComponent = shallowRef(null)
const componentProps = ref({})

// 获取URL参数
function getQueryParams() {
  const urlParams = new URLSearchParams(window.location.search)
  const params = {}
  for (const [key, value] of urlParams.entries()) {
    params[key] = value
  }
  return params
}

onMounted(() => {
  console.log('App.vue mounted');
  console.log('window.previewParams:', window.previewParams);
  
  // 首先检查全局参数
  if (window.previewParams && window.previewParams.filePath) {
    const { filePath, fileType, fileName,fileId } = window.previewParams
    console.log('使用全局参数:', { filePath, fileType, fileName,fileId });
    
    if (fileType === 'excel') {
      currentComponent.value = ExcelPreview
      componentProps.value = { filePath,fileType, fileName, fileId }
    } else {
      currentComponent.value = PdfViewer
      componentProps.value = { filePath,fileType, fileName, fileId }
    }
    return
  }
  
  // 检查初始参数
  if (props.initialParams && props.initialParams.filePath) {
    const { filePath, fileType, fileName,fileId } = props.initialParams
    console.log('使用初始参数:', { filePath, fileType, fileName,fileId });
    
    if (fileType === 'excel') {
      currentComponent.value = ExcelPreview
      componentProps.value = { filePath,fileType, fileName, fileId }
    } else {
      currentComponent.value = PdfViewer
      componentProps.value = { filePath,fileType, fileName, fileId }
    }
    return
  }

  // 如果没有初始参数，从URL获取
  const params = getQueryParams()
  const { filePath, fileType, fileName, convertToPdf, url,fileId } = params
  console.log('URL参数:', params);
  
  // 处理URL参数中的额外信息
  let finalFilePath = filePath;
  if (url && !finalFilePath) {
    finalFilePath = url;
  }
  
  if (fileId && !finalFilePath) {
    finalFilePath = `/api/download?file_id=${fileId}`;
  }
  
  if (finalFilePath) {
    let fileExt = '';
    try {
      // 尝试从文件路径中提取扩展名
      fileExt = finalFilePath.split('.').pop().toLowerCase();
    } catch (e) {
      console.error('无法提取文件扩展名:', e);
    }
    
    const isExcel = fileType === 'excel' || fileExt === 'xls' || fileExt === 'xlsx';
    
    if (isExcel && convertToPdf !== 'true') {
      console.log('加载Excel预览组件:', finalFilePath);
      currentComponent.value = ExcelPreview;
      componentProps.value = { filePath: finalFilePath, fileName,fileType,fileId };
    } else {
      console.log('加载PDF预览组件:', finalFilePath);
      currentComponent.value = PdfViewer;
      componentProps.value = { filePath: finalFilePath, fileName,fileType,fileId };
    }
  } else {
    console.error('无法找到有效的文件路径');
  }
})
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
}

.app-container {
  width: 100%;
  height: 100vh;
  background-color: #f5f5f5;
}
</style> 