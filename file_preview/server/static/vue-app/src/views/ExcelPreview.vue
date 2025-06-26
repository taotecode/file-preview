<template>
    <div class="excel-preview-container">
        <div class="excel-container" v-loading="loading">
            <vue-office-excel v-if="filePath && !error" :src="filePath" :options="options" @rendered="handleRendered"
                @error="handleError" class="excel-viewer" />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import VueOfficeExcel from '@vue-office/excel'
import { ElMessage, ElAlert, ElButton } from 'element-plus'
//引入相关样式
import '@vue-office/excel/lib/index.css'

const props = defineProps({
    filePath: {
        type: String,
        required: true
    },
    fileName: {
        type: String,
        default: ''
    },
    fileType: {
        type: String,
        default: 'excel'
    },
    fileId: {
        type: String,
        default: ''
    }
})

const loading = ref(true)
const error = ref(null)
const options = ref({
    // 添加一些配置选项
    xls: false,       //预览xlsx文件设为false；预览xls文件设为true
    minColLength: 0,  // excel最少渲染多少列，如果想实现xlsx文件内容有几列，就渲染几列，可以将此值设置为0.
    minRowLength: 0,  // excel最少渲染多少行，如果想实现根据xlsx实际函数渲染，可以将此值设置为0.
    widthOffset: 10,  //如果渲染出来的结果感觉单元格宽度不够，可以在默认渲染的列表宽度上再加 Npx宽
    heightOffset: 10, //在默认渲染的列表高度上再加 Npx高
    beforeTransformData: (workbookData) => { return workbookData }, //底层通过exceljs获取excel文件内容，通过该钩子函数，可以对获取的excel文件内容进行修改，比如某个单元格的数据显示不正确，可以在此自行修改每个单元格的value值。
    transformData: (workbookData) => { return workbookData }, //将获取到的excel数据进行处理之后且渲染到页面之前，可通过transformData对即将渲染的数据及样式进行修改，此时每个单元格的text值就是即将渲染到页面上的内容
})



function handleRendered() {
    loading.value = false
    console.log('Excel文件渲染完成')
}

function handleError(err) {
    loading.value = false
    error.value = `Excel文件加载失败: ${err.message || '未知错误'}`
    console.error('Excel预览错误:', err)
    ElMessage.error('Excel文件加载失败')
}


onMounted(() => {
    console.log('ExcelPreview mounted, filePath:', props.filePath)
    if (!props.filePath) {
        error.value = '未提供有效的文件路径'
        loading.value = false
    }
})
</script>

<style scoped>
.excel-preview-container {
    width: 100%;
    height: 100vh;
}

.excel-container {
    width: 100%;
    height: 100%;
    background-color: #fff;
}

.excel-viewer {
    width: 100%;
    height: 100%;
}
</style>
