<template>
  <div class="table-wrapper" :class="{'h-full': isFullHeight}">
    <!-- 表格容器始终存在，但在loading或error时被覆盖 -->
    <div ref="tableContainer" class="table-container" :style="containerStyle"></div>
    
    <!-- 加载状态和错误提示作为覆盖层 -->
    <div v-if="loading" class="overlay flex items-center justify-center p-4">
      <div class="spinner"></div>
      <span class="ml-2">加载中...</span>
    </div>
    <div v-else-if="error" class="overlay error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, defineEmits } from 'vue';
import { createSpreadsheet, convertToSpreadsheetData, loadData, loadMultiSheets } from '../utils/spreadsheet-utils';
import type { TableData } from '../utils/excel-utils';

const props = defineProps({
  data: {
    type: Object as () => TableData | null,
    default: null
  },
  multipleSheets: {
    type: Boolean,
    default: false
  },
  sheetsData: {
    type: Object as () => Record<string, TableData>,
    default: () => ({})
  },
  sheetNames: {
    type: Array as () => string[],
    default: () => []
  },
  height: {
    type: [Number, String],
    default: '100%'
  },
  isFullHeight: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['error', 'rendered']);

const tableContainer = ref<HTMLElement | null>(null);
const spreadsheetInstance = ref<any>(null);
const loading = ref(true);
const error = ref<string | null>(null);

// 计算容器样式
const containerStyle = computed(() => {
  if (typeof props.height === 'number') {
    return { height: `${props.height}px` };
  }
  return { height: props.height };
});

// 创建电子表格实例
function createSpreadsheetInstance(): boolean {
  if (!tableContainer.value) {
    console.error('表格容器元素不存在');
    error.value = '表格容器初始化失败';
    emit('error', '表格容器初始化失败');
    return false;
  }

  try {
    // 清空容器内容，避免重复渲染
    tableContainer.value.innerHTML = '';
    
    // 配置选项
    const options = {
      showBottomBar: props.multipleSheets, // 多工作表时显示底部工作表切换栏
      height: props.height,
      view: {
        height: () => typeof props.height === 'number' ? props.height : '100%',
      },
      mode: 'read', // 设置为只读模式
      showToolbar: false, // 不显示工具栏
      showGrid: true,     // 显示网格线
      showContextmenu: false, // 不显示右键菜单
      row: {
        len: 100,
        height: 25,
      },
      col: {
        len: 26,
        width: 100,
        indexWidth: 60,
        minWidth: 60,
      },
      style: {
        // 默认样式，避免样式丢失时的显示问题
        bgcolor: '#ffffff',
        align: 'left',
        valign: 'middle',
        textwrap: false,
        underline: false,
        color: '#333333',
        font: {
          name: 'Microsoft YaHei',
          size: 10,
          bold: false,
          italic: false,
        },
      }
    };
    
    console.log('使用选项创建电子表格:', options);
    
    spreadsheetInstance.value = createSpreadsheet(tableContainer.value, options);

    if (!spreadsheetInstance.value) {
      throw new Error('创建电子表格实例失败');
    }
    
    // 设置中文本地化
    try {
      spreadsheetInstance.value.locale('zh-cn');
    } catch (e) {
      console.warn('设置语言失败:', e);
    }

    // 添加事件处理
    setupEventListeners();
    
    return true;
  } catch (e) {
    console.error('创建电子表格实例失败:', e);
    error.value = `创建电子表格实例失败: ${e instanceof Error ? e.message : String(e)}`;
    emit('error', `创建电子表格实例失败: ${e instanceof Error ? e.message : String(e)}`);
    return false;
  }
}

// 设置事件监听
function setupEventListeners() {
  if (!spreadsheetInstance.value) return;
  
  // 重写渲染方法，确保data始终有值
  const originalRender = spreadsheetInstance.value.sheet.render;
  spreadsheetInstance.value.sheet.render = function() {
    // 确保this.data存在
    if (!this.data) {
      console.warn('工作表数据为空，使用默认空数据');
      this.data = { rows: {}, cols: {}, merges: [] };
    }
    return originalRender.apply(this, arguments);
  };
  
  // 监听工作表切换事件
  spreadsheetInstance.value.on('sheet-show', (index: number) => {
    console.log('切换到工作表:', index);
    
    // 确保工作表数据有效
    const data = spreadsheetInstance.value.getData();
    if (Array.isArray(data) && data[index] && !data[index].rows) {
      console.warn(`工作表 ${index} 数据格式不正确，修复中`);
      data[index].rows = data[index].rows || {};
      spreadsheetInstance.value.loadData(data);
    }
  });
  
  // 监听数据变化事件
  spreadsheetInstance.value.on('changed', (...args: any[]) => {
    console.log('表格数据变更:', args);
  });
  
  // 监听单元格选择事件
  spreadsheetInstance.value.on('cell-selected', (cell: any, ri: number, ci: number) => {
    console.log('选中单元格:', ri, ci, cell);
  });

  // 监听单元格区域选择事件
  spreadsheetInstance.value.on('cells-selected', (cell: any, { sri, sci, eri, eci }: any) => {
    console.log('选中单元格区域:', { sri, sci, eri, eci });
  });
}

// 统一渲染工作表方法
function renderSpreadsheet() {
  console.log('开始渲染电子表格', props.multipleSheets ? '多工作表模式' : '单工作表模式');
  loading.value = true;
  error.value = null;
  
  // 1. 创建电子表格实例
  if (!createSpreadsheetInstance()) {
    loading.value = false;
    return;
  }
  
  // 2. 渲染工作表
  try {
    renderSheets();
    
    // 渲染完成
    loading.value = false;
    emit('rendered');
  } catch (e) {
    console.error('渲染电子表格失败:', e);
    error.value = `渲染电子表格失败: ${e instanceof Error ? e.message : String(e)}`;
    emit('error', `渲染电子表格失败: ${e instanceof Error ? e.message : String(e)}`);
    loading.value = false;
  }
}

// 统一的工作表渲染方法 - 处理所有场景
function renderSheets() {
  if (!spreadsheetInstance.value) return;
  
  // 1. 确定数据源
  let sheetsMap: Record<string, TableData> = {};
  
  // 从sheetsData获取数据 (优先级最高)
  if (props.multipleSheets && Object.keys(props.sheetsData).length > 0) {
    console.log('从SheetsData渲染多个工作表:', Object.keys(props.sheetsData));
    sheetsMap = { ...props.sheetsData };
  }
  // 从data.sheets获取数据
  else if (props.data && props.multipleSheets && props.data.sheets && props.data.sheets.length > 0) {
    console.log('从data.sheets渲染多个工作表:', props.data.sheets.length);
    
    // 将sheets数组转换为map对象
    props.data.sheets.forEach(sheet => {
      sheetsMap[sheet.name] = sheet;
    });
  }
  // 从单个data获取数据
  else if (props.data) {
    console.log('渲染单个工作表');
    sheetsMap = { [props.data.name || 'Sheet1']: props.data };
  }
  // 没有数据可渲染
  else {
    throw new Error('没有数据可渲染');
  }
  
  // 2. 检查数据有效性
  if (Object.keys(sheetsMap).length === 0) {
    throw new Error('没有工作表数据可渲染');
  }
  
  // 3. 预处理所有工作表数据
  Object.entries(sheetsMap).forEach(([sheetName, sheetData]) => {
    // 确保每个工作表有rows属性
    if (!sheetData.rows) {
      sheetData.rows = {};
    }
    
    // 记录合并单元格信息（如果有）
    if (sheetData.merges && sheetData.merges.length > 0) {
      console.log(`工作表 ${sheetName} 有 ${sheetData.merges.length} 个合并单元格`);
    }
  });
  
  // 4. 加载工作表数据
  let result: boolean;
  
  // 多工作表模式
  if (props.multipleSheets || Object.keys(sheetsMap).length > 1) {
    // 多工作表模式时先清空
    spreadsheetInstance.value.loadData([]);
    result = loadMultiSheets(spreadsheetInstance.value, sheetsMap);
  } 
  // 单工作表模式
  else {
    const singleSheetData = Object.values(sheetsMap)[0];
    result = loadData(spreadsheetInstance.value, singleSheetData);
  }
  
  if (!result) {
    throw new Error('加载表格数据失败');
  }
  
  // 5. 数据验证与修复
  if (props.multipleSheets || Object.keys(sheetsMap).length > 1) {
    // 确保样式和合并单元格正确应用
    spreadsheetInstance.value.reRender();
    
    // 获取渲染后的数据进行验证
    const renderedData = spreadsheetInstance.value.getData();
    
    if (Array.isArray(renderedData)) {
      // 确保每个工作表都有rows属性
      let needsReload = false;
      
      renderedData.forEach((sheet, index) => {
        if (!sheet.rows) {
          sheet.rows = {};
          needsReload = true;
          console.warn(`修复工作表 ${index} 缺少的rows属性`);
        }
        
        console.log(`工作表 ${index} 信息:`, {
          name: sheet.name,
          mergesCount: sheet.merges ? sheet.merges.length : 0
        });
      });
      
      // 如果有修复，重新加载数据
      if (needsReload) {
        spreadsheetInstance.value.loadData(renderedData);
      }
    }
  }
  
  console.log('工作表渲染完成');
}

// 组件挂载时初始化表格
onMounted(() => {
  console.log('TableRenderer组件挂载');
  console.log('- sheetsData:', props.sheetsData);
  console.log('- multipleSheets:', props.multipleSheets);
  
  // 直接渲染，不使用延迟
  renderSpreadsheet();
});

// 组件卸载前清理资源
onBeforeUnmount(() => {
  if (spreadsheetInstance.value) {
    try {
      spreadsheetInstance.value.destroy();
    } catch (e) {
      console.warn('销毁电子表格实例失败:', e);
    }
    spreadsheetInstance.value = null;
  }
});
</script>

<style scoped>
.table-wrapper {
  width: 100%;
  position: relative;
  min-height: 300px;
}

.table-container {
  width: 100%;
  overflow: auto;
  height: 100%;
  min-height: 300px;
}

.h-full {
  height: 100%;
}

/* 覆盖层样式 */
.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: white;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-message {
  color: #f56c6c;
  padding: 12px;
  background-color: #fef0f0;
  border-radius: 4px;
  margin: 10px 0;
}

.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #1890ff;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 表格样式覆盖 */
:deep(.x-spreadsheet) {
  border: 1px solid #e0e0e0;
  box-shadow: none;
  height: 100% !important;
}

:deep(.x-spreadsheet-sheet) {
  height: calc(100% - 35px) !important;
}
</style> 