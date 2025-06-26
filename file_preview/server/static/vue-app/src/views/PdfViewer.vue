<template>
  <div class="pdf-container">
    <object :data="pdfUrl" type="application/pdf" width="100%" height="100%">
      <p>无法显示PDF文件，请<a :href="pdfUrl" target="_blank">下载</a>后查看</p>
    </object>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  filePath: {
    type: String,
    required: true
  }
})

const pdfUrl = ref('')

onMounted(() => {
  pdfUrl.value = props.filePath
})
</script>

<style scoped>
.pdf-container {
  width: 100%;
  height: 100vh;
}
</style> 