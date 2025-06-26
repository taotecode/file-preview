<template>
  <div class="worksheet-selector">
    <el-tabs 
      v-model="currentSheet" 
      type="card" 
      class="worksheet-tabs"
      @tab-change="handleTabChange"
    >
      <el-tab-pane 
        v-for="sheet in worksheets" 
        :key="sheet" 
        :label="sheet" 
        :name="sheet"
      />
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElTabs, ElTabPane } from 'element-plus'
import type { TabPaneName } from 'element-plus'

// 定义props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  worksheets: {
    type: Array as () => string[],
    default: () => []
  }
})

// 定义事件
const emit = defineEmits(['update:modelValue', 'change'])

// 当前选中的工作表
const currentSheet = ref(props.modelValue || '')

// 处理标签页变化
function handleTabChange(tabName: TabPaneName) {
  const sheetName = String(tabName)
  currentSheet.value = sheetName
  emit('update:modelValue', sheetName)
  emit('change', sheetName)
}

// 监听modelValue变化
watch(() => props.modelValue, (newVal) => {
  if (newVal !== currentSheet.value) {
    currentSheet.value = newVal
  }
}, { immediate: true })

// 监听worksheets变化
watch(() => props.worksheets, (newVal) => {
  if (newVal.length > 0 && !currentSheet.value) {
    // 当工作表列表变化且当前未选择工作表时，自动选择第一个
    currentSheet.value = newVal[0]
    emit('update:modelValue', currentSheet.value)
    emit('change', currentSheet.value)
  } else if (newVal.length > 0 && !newVal.includes(currentSheet.value)) {
    // 当工作表列表变化且当前选择的工作表不在列表中时，自动选择第一个
    currentSheet.value = newVal[0]
    emit('update:modelValue', currentSheet.value)
    emit('change', currentSheet.value)
  }
}, { immediate: true })
</script>

<style scoped>
.worksheet-selector {
  margin-bottom: 12px;
}

.worksheet-tabs {
  width: 100%;
  overflow-x: auto;
  white-space: nowrap;
}

:deep(.el-tabs__header) {
  margin: 0;
}

:deep(.el-tabs__item) {
  padding: 0 16px;
  height: 32px;
  line-height: 32px;
  font-size: 14px;
}

/* 在较窄的屏幕上适配 */
@media (max-width: 768px) {
  :deep(.el-tabs__item) {
    padding: 0 10px;
    font-size: 13px;
  }
}
</style> 