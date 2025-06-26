/**
 * x-data-spreadsheet工具类
 * 处理Excel数据到x-data-spreadsheet格式的转换
 */

import Spreadsheet from 'x-data-spreadsheet';
import type { TableData, CellStyle, CellData } from './excel-utils';
import { indexToColName } from './excel-utils';

/**
 * 初始化电子表格实例
 * @param container 容器元素或容器ID
 * @param options 表格选项
 */
export function createSpreadsheet(container: HTMLElement | string, options: any = {}): any {
    try {
        // 配置电子表格
        const defaultOptions = {
            view: {
                height: () => options.height || 600,
                width: () => options.width || '100%',
            },
            row: {
                len: options.rowCount || 100,
                height: 25,
            },
            col: {
                len: options.colCount || 26,
                width: 100,
                indexWidth: 60,
                minWidth: 60,
            },
            style: {
                // 默认样式
                bgcolor: '#ffffff',
                color: '#333333',
                align: 'left',
                valign: 'middle',
                textwrap: false,
                strike: false,
                underline: false,
                bold: false,
                italic: false,
                fontSize: 10,
            },
            showToolbar: options.showToolbar ?? false,
            showGrid: true,
            showContextmenu: false,
            showBottomBar: options.showBottomBar ?? true, // 默认显示底部工作表切换栏
            mode: 'read', // 设置为只读模式
        };

        // 创建电子表格实例，根据参数类型确定如何传递容器
        const spreadsheet = typeof container === 'string'
            ? new Spreadsheet(`#${container}`, { ...defaultOptions, ...options })
            : new Spreadsheet(container, { ...defaultOptions, ...options });

        // 隐藏默认工具栏
        if (!options.showToolbar) {
            try {
                const toolbar = document.querySelector('.x-spreadsheet-toolbar');
                if (toolbar) {
                    (toolbar as HTMLElement).style.display = 'none';
                }
            } catch (e) {
                console.warn('隐藏工具栏出错:', e);
            }
        }

        // 控制底部工作表切换栏的显示
        try {
            const bottomBar = document.querySelector('.x-spreadsheet-bottombar');
            if (bottomBar) {
                (bottomBar as HTMLElement).style.display = options.showBottomBar ? 'flex' : 'none';
            }
        } catch (e) {
            console.warn('设置底部工作表切换栏显示状态出错:', e);
        }

        // 设置中文语言
        try {
            // @ts-ignore
            if (window.x_spreadsheet && window.x_spreadsheet.locale) {
                // @ts-ignore
                window.x_spreadsheet.locale('zh-cn');
            }
        } catch (e) {
            console.warn('设置语言失败:', e);
        }

        console.log('电子表格实例创建成功');
        return spreadsheet;
    } catch (error) {
        console.error('创建电子表格实例失败:', error);
        return null;
    }
}

/**
 * 将单元格样式转换为x-data-spreadsheet格式
 * @param style 单元格样式
 */
function convertStyle(style: CellStyle): any {
    if (!style) return {};

    const result: any = {};

    // 基本样式
    if (style.bold !== undefined) result.bold = style.bold;
    if (style.italic !== undefined) result.italic = style.italic;
    if (style.underline !== undefined) result.underline = style.underline;
    if (style.color !== undefined) result.color = style.color;
    // 注意: XSpreadsheet使用的是bgColor而不是bgcolor
    if (style.bgcolor !== undefined) result.bgcolor = style.bgcolor;
    
    // 字体大小转换 (pt -> px，大约1pt = 1.33px)
    if (style.fontSize !== undefined) {
        const fontSizeInPx = Math.round(style.fontSize * 1.33);
        result.fontSize = fontSizeInPx;
    }
    
    if (style.textwrap !== undefined) result.textwrap = style.textwrap;

    // 对齐方式
    if (style.align !== undefined) result.align = style.align;
    
    // 垂直对齐映射
    if (style.valign !== undefined) {
        const valignMap: Record<string, string> = {
            'top': 'top',
            'middle': 'middle',
            'bottom': 'bottom',
            'center': 'middle', // Excel可能使用center，x-data-spreadsheet使用middle
            'distributed': 'middle',
            'justify': 'middle'
        };
        result.valign = valignMap[style.valign] || 'middle';
    }

    // 边框 - XSpreadsheet使用特殊格式
    if (style.border) {
        // 在x-data-spreadsheet中，边框使用格式：
        // border: { bottom: ["thick", "#000"] }
        const border: any = {};
        
        ['top', 'bottom', 'left', 'right'].forEach(direction => {
            if (style.border?.[direction as keyof typeof style.border]) {
                const borderStyle = style.border[direction as keyof typeof style.border];
                if (borderStyle) {
                    // 转换为XSpreadsheet期望的格式 [style, color]
                    border[direction] = [
                        borderStyle.style || 'thin', 
                        borderStyle.color || '#000000'
                    ];
                }
            }
        });
        
        if (Object.keys(border).length > 0) {
            result.border = border;
        }
    }

    // border2属性(样例中有)
    if (style.border2) {
        result.border2 = style.border2;
    }

    // 处理完整字体对象
    const fontObj: any = {};
    let hasFontProperties = false;
    
    // 将字体大小转为像素
    if (style.fontSize !== undefined) {
        fontObj.size = Math.round(style.fontSize * 1.33);
        hasFontProperties = true;
    } else if (style.font?.size !== undefined) {
        fontObj.size = Math.round(style.font.size * 1.33);
        hasFontProperties = true;
    }
    
    // 从font对象获取更多属性
    if (style.font) {
        if (style.font.name) {
            fontObj.name = style.font.name;
            hasFontProperties = true;
        } else {
            fontObj.name = 'Microsoft YaHei'; // 默认字体
        }
        
        if (style.font.bold !== undefined) {
            fontObj.bold = style.font.bold;
            hasFontProperties = true;
        } else if (style.bold !== undefined) {
            fontObj.bold = style.bold;
            hasFontProperties = true;
        }
        
        if (style.font.italic !== undefined) {
            fontObj.italic = style.font.italic;
            hasFontProperties = true;
        } else if (style.italic !== undefined) {
            fontObj.italic = style.italic;
            hasFontProperties = true;
        }
        
        if (style.font.color) {
            // 将复杂的颜色对象转换为简单字符串
            if (typeof style.font.color === 'object') {
                // 优先使用style.color
                if (style.color) {
                    fontObj.color = style.color;
                } 
                // 尝试从font.color对象中提取
                else if (style.font.color.rgb) {
                    fontObj.color = `#${style.font.color.rgb}`;
                } else if (style.font.color.argb) {
                    fontObj.color = `#${style.font.color.argb.substring(2)}`;
                } else if (style.font.color.theme !== undefined) {
                    // 样例中使用了theme: 0
                    if (style.font.color.theme === 0) {
                        fontObj.color = '#FFFFFF';
                    }
                }
            } else {
                fontObj.color = style.font.color;
            }
            hasFontProperties = true;
        }
    }
    
    // 如果有字体属性，添加到结果
    if (hasFontProperties) {
        result.font = fontObj;
    }
    
    // 处理fill/alignment等完整对象属性
    if (style.fill) {
        // 保留fill属性，因为样例中使用了
        result.fill = style.fill;
    }
    
    if (style.alignment) {
        // 保留alignment属性，因为样例中使用了
        result.alignment = style.alignment;
    }

    return result;
}

/**
 * 将表格单元格坐标转换为Excel格式的单元格引用 (例如: A1, B2)
 * @param row 行索引 (从0开始)
 * @param col 列索引 (从0开始)
 * @returns Excel格式的单元格引用
 */
function cellRef(row: number, col: number): string {
    return `${indexToColName(col)}${row + 1}`;
}

/**
 * 将合并单元格格式转换为Excel格式的单元格范围 (例如: A1:B2)
 * @param startRow 起始行索引 (从0开始)
 * @param startCol 起始列索引 (从0开始)
 * @param endRow 结束行索引 (从0开始)
 * @param endCol 结束列索引 (从0开始)
 * @returns Excel格式的单元格范围
 */
function mergeRef(startRow: number, startCol: number, endRow: number, endCol: number): string {
    return `${cellRef(startRow, startCol)}:${cellRef(endRow, endCol)}`;
}

/**
 * 将TableData转换为x-data-spreadsheet格式
 * @param data TableData对象
 * @param sheetName 工作表名称
 */
export function convertToSpreadsheetData(data: TableData, sheetName: string = 'Sheet1'): any {
    if (!data) return { name: sheetName, rows: {}, cols: {}, styles: [], merges: [] };

    // 记录单元格数量用于调试
    const cellCount = data.cells ? Object.keys(data.cells).length : 0;
    console.log(`转换工作表 "${sheetName}" 数据, 有 ${cellCount} 个单元格`);
    console.log(`data:`, data);

    // x-data-spreadsheet格式：
    // {
    //   name: "sheet1",
    //   styles: [样式数组],
    //   rows: {
    //     0: { cells: { 0: { text: "A1", style: 0 }, 1: { text: "B1", style: 1 } } },
    //     1: { cells: { 0: { text: "A2" }, 1: { text: "B2" } } }
    //   },
    //   cols: { 0: { width: 100 }, 1: { width: 120 } },
    //   merges: ["A1:B1", "C1:D3"]
    // }

    // 创建工作表数据结构
    const sheetData: any = {
        name: sheetName || data.name || 'Sheet1',
        styles: [],        // 样式数组
        rows: {},          // 行数据
        cols: {},          // 列数据
        merges: [],        // 合并单元格
        media: []          // 媒体数据
    };

    // 样式映射表，用于去重
    const styleMap = new Map();
    
    // 处理列宽
    if (data.cols && typeof data.cols === 'object') {
        Object.entries(data.cols).forEach(([colIndex, colData]) => {
            const colIdx = parseInt(colIndex);
            if (!isNaN(colIdx) && colData.width) {
                // 设置列宽
                sheetData.cols[colIdx] = {
                    width: colData.width * 8  // 根据需要调整系数
                };
            }
        });
    }

    // 处理单元格数据 - 优先使用data.cells
    if (data.cells && typeof data.cells === 'object') {
        // 单元格按行分组
        const rowCells: Record<number, Record<number, CellData>> = {};
        
        // 先将单元格按行分组
        Object.entries(data.cells).forEach(([key, cellData]) => {
            if (!key.includes('_')) return;

            const [rowStr, colStr] = key.split('_');
            const row = parseInt(rowStr);
            const col = parseInt(colStr);

            if (isNaN(row) || isNaN(col)) return;
            
            // 初始化行
            if (!rowCells[row]) {
                rowCells[row] = {};
            }
            
            // 将单元格添加到对应行
            rowCells[row][col] = cellData;
        });
        
        // 处理每一行数据
        Object.entries(rowCells).forEach(([rowIndex, cells]) => {
            const row = parseInt(rowIndex);
            
            // 获取行高
            const rowHeight = data.rows && data.rows[row] ? data.rows[row].height : undefined;
            
            // 创建行对象
            const rowData: any = {
                cells: {},
            };
            
            // 设置行高 (pt -> px 转换)
            if (rowHeight) {
                rowData.height = Math.round(rowHeight * 1.33);
            }
            
            // 处理该行的所有单元格
            Object.entries(cells).forEach(([colIndex, cellData]) => {
                const col = parseInt(colIndex);
                
                // 处理单元格样式
                let styleId = -1;
                if (cellData.style) {
                    const styleObj = typeof cellData.style === 'object' ? 
                        convertStyle(cellData.style as CellStyle) : {};
                    
                    // 检查是否已存在相同样式
                    const styleKey = JSON.stringify(styleObj);
                    if (styleMap.has(styleKey)) {
                        styleId = styleMap.get(styleKey);
                    } else {
                        styleId = sheetData.styles.length;
                        sheetData.styles.push(styleObj);
                        styleMap.set(styleKey, styleId);
                    }
                }

                // 创建单元格数据
                const cell: any = {};
                
                // 添加文本内容
                if (cellData.text !== undefined) {
                    cell.text = cellData.text;
                }
                
                // 添加样式引用
                if (styleId >= 0) {
                    cell.style = styleId;
                }
                
                // 添加链接
                if (cellData.link) {
                    cell.link = cellData.link;
                }
                
                // 添加合并信息
                if (cellData.merge && Array.isArray(cellData.merge) && cellData.merge.length === 2) {
                    cell.merge = cellData.merge;
                    
                    // 记录合并单元格到字符串格式，以便下面统一处理
                    const [rowspan, colspan] = cellData.merge;
                    if (rowspan > 1 || colspan > 1) {
                        // 添加合并单元格信息，格式为A1:B2
                        const mergeStr = mergeRef(row, col, row + rowspan - 1, col + colspan - 1);
                        if (!sheetData.merges.includes(mergeStr)) {
                            sheetData.merges.push(mergeStr);
                        }
                    }
                }
                
                // 将单元格添加到行数据中
                rowData.cells[col] = cell;
            });
            
            // 将行数据添加到表格数据中
            sheetData.rows[row] = rowData;
        });
    } else if (data.rows) {
        // 如果没有cells属性，使用rows属性构建
        Object.entries(data.rows).forEach(([rowIndex, rowData]) => {
            const row = parseInt(rowIndex);
            
            // 创建行对象
            const newRowData: any = {
                cells: {},
            };
            
            // 设置行高 (pt -> px 转换)
            if (rowData.height) {
                newRowData.height = Math.round(rowData.height * 1.33);
            }
            
            // 处理该行的所有单元格
            if (rowData.cells) {
                Object.entries(rowData.cells).forEach(([colIndex, cellData]) => {
                    const col = parseInt(colIndex);
                    
                    // 处理单元格样式
                    let styleId = -1;
                    if (cellData.style) {
                        const styleObj = typeof cellData.style === 'object' ? 
                            convertStyle(cellData.style as CellStyle) : {};
                        
                        // 检查是否已存在相同样式
                        const styleKey = JSON.stringify(styleObj);
                        if (styleMap.has(styleKey)) {
                            styleId = styleMap.get(styleKey);
                        } else {
                            styleId = sheetData.styles.length;
                            sheetData.styles.push(styleObj);
                            styleMap.set(styleKey, styleId);
                        }
                    }

                    // 创建单元格数据
                    const cell: any = {};
                    
                    // 添加文本内容
                    if (cellData.text !== undefined) {
                        cell.text = cellData.text;
                    }
                    
                    // 添加样式引用
                    if (styleId >= 0) {
                        cell.style = styleId;
                    }
                    
                    // 添加链接
                    if (cellData.link) {
                        cell.link = cellData.link;
                    }
                    
                    // 添加合并信息
                    if (cellData.merge && Array.isArray(cellData.merge) && cellData.merge.length === 2) {
                        cell.merge = cellData.merge;
                        
                        // 记录合并单元格到字符串格式，以便下面统一处理
                        const [rowspan, colspan] = cellData.merge;
                        if (rowspan > 1 || colspan > 1) {
                            // 添加合并单元格信息，格式为A1:B2
                            const mergeStr = mergeRef(row, col, row + rowspan - 1, col + colspan - 1);
                            if (!sheetData.merges.includes(mergeStr)) {
                                sheetData.merges.push(mergeStr);
                                console.log(`从单元格合并属性添加合并单元格: ${row},${col} [${rowspan},${colspan}] => ${mergeStr}`);
                            }
                        }
                    }
                    
                    // 将单元格添加到行数据中
                    newRowData.cells[col] = cell;
                });
            }
            
            // 将行数据添加到表格数据中
            sheetData.rows[row] = newRowData;
        });
    }
    
    // 处理合并单元格（如果有额外的合并单元格定义）
    if (data.merges && Array.isArray(data.merges) && data.merges.length > 0) {
        console.log(`处理 ${data.merges.length} 个合并单元格定义，来自 TableData.merges`);
        
        data.merges.forEach(merge => {
            if (merge.sri !== undefined && 
                merge.sci !== undefined && 
                merge.eri !== undefined && 
                merge.eci !== undefined) {
                
                // 将合并单元格转换为Excel格式的单元格范围 (例如: A1:B2)
                const mergeString = mergeRef(merge.sri, merge.sci, merge.eri, merge.eci);
                
                // 检查是否已经添加过这个合并单元格
                if (!sheetData.merges.includes(mergeString)) {
                    sheetData.merges.push(mergeString);
                    console.log(`从TableData.merges添加合并单元格: sri=${merge.sri},sci=${merge.sci},eri=${merge.eri},eci=${merge.eci} => ${mergeString}`);
                    
                    // 同时在主单元格设置merge属性，提高兼容性
                    const row = merge.sri;
                    const col = merge.sci;
                    
                    if (sheetData.rows[row] && sheetData.rows[row].cells && sheetData.rows[row].cells[col]) {
                        const rowSpan = merge.eri - merge.sri + 1;
                        const colSpan = merge.eci - merge.sci + 1;
                        
                        // 为主单元格添加合并信息
                        sheetData.rows[row].cells[col].merge = [rowSpan, colSpan];
                    }
                }
            }
        });
    }

    // 输出生成的行数据，用于调试
    console.log(`工作表 "${sheetName}" 转换后的行数量: ${Object.keys(sheetData.rows).length}, 样式数量: ${sheetData.styles.length}`);

    return sheetData;
}

/**
 * 加载表格数据到电子表格实例
 * @param spreadsheet 电子表格实例
 * @param data 表格数据
 * @param sheetName 工作表名称
 */
export function loadData(spreadsheet: any, data: TableData, sheetName: string = 'Sheet1'): boolean {
    try {
        if (!spreadsheet || !data) {
            console.error('加载数据时缺少必要参数');
            return false;
        }

        // 转换数据
        const sheetData = convertToSpreadsheetData(data, sheetName);
        
        // 确保merges是字符串数组格式（如 ["A1:B2", "C3:D4"]）
        if (Array.isArray(sheetData.merges)) {
            sheetData.merges = sheetData.merges.map((merge: any) => {
                // 已经是字符串格式的直接返回
                if (typeof merge === 'string' && /^[A-Z]+[0-9]+:[A-Z]+[0-9]+$/.test(merge)) {
                    return merge;
                }
                
                // 处理数组格式 [startRow, startCol, rowspan, colspan]
                if (Array.isArray(merge) && merge.length === 4) {
                    const [startRow, startCol, rowspan, colspan] = merge;
                    return mergeRef(startRow, startCol, startRow + rowspan - 1, startCol + colspan - 1);
                }
                
                // 处理对象格式 {sri, sci, eri, eci}
                if (typeof merge === 'object' && merge.sri !== undefined && merge.sci !== undefined &&
                    merge.eri !== undefined && merge.eci !== undefined) {
                    return mergeRef(merge.sri, merge.sci, merge.eri, merge.eci);
                }
                
                console.warn('无法识别的合并单元格格式:', merge);
                return null;
            }).filter(Boolean); // 过滤掉null值
        }
        
        // 加载数据到表格 - x-data-spreadsheet适用格式
        const loadData = [sheetData];  // 使用数组格式
        
        // 输出数据结构摘要
        const cellCount = data.cells ? Object.keys(data.cells).length : 0;
        console.log(`单表加载数据结构: ${sheetName}, 单元格数: ${cellCount}, 合并单元格数: ${sheetData.merges.length}`);

        console.log('loadData', loadData);
        
        
        // 加载数据
        spreadsheet.loadData(loadData);
        
        // 强制重新渲染
        try {
            setTimeout(() => {
                spreadsheet.reRender();
                
                // 验证数据是否正确加载
                const loadedData = spreadsheet.getData();
                if (Array.isArray(loadedData) && loadedData.length > 0) {
                    const firstSheet = loadedData[0];
                    console.log('验证数据加载:', {
                        name: firstSheet.name,
                        rows: Object.keys(firstSheet.rows || {}).length,
                        merges: firstSheet.merges ? firstSheet.merges.length : 0
                    });
                    
                    // 输出合并单元格样本
                    if (firstSheet.merges && firstSheet.merges.length > 0) {
                        console.log('合并单元格样本:', firstSheet.merges.slice(0, 3));
                    }
                }
            }, 100);
        } catch (e) {
            console.warn('重新渲染失败:', e);
        }

        console.log('表格数据加载成功');
        return true;
    } catch (error) {
        console.error('加载表格数据失败:', error);
        return false;
    }
}

/**
 * 创建多个工作表
 * @param spreadsheet 电子表格实例 
 * @param sheetDataMap 工作表数据映射
 */
export function loadMultiSheets(spreadsheet: any, sheetDataMap: Record<string, TableData>): boolean {
    try {
        if (!spreadsheet || !sheetDataMap) {
            console.error('加载多工作表时缺少必要参数');
            return false;
        }

        console.log('准备加载多工作表:', Object.keys(sheetDataMap));
        
        // 清空所有工作表数据，防止旧数据干扰
        const sheetsArray: any[] = [];
        
        // 转换每个工作表的数据
        Object.entries(sheetDataMap).forEach(([sheetName, tableData]) => {
            // 转换工作表数据到XSpreadsheet格式
            const sheetData = convertToSpreadsheetData(tableData, sheetName);
            
            // 检查工作表数据完整性
            if (!sheetData.rows) sheetData.rows = {};
            if (!sheetData.styles) sheetData.styles = [];
            if (!sheetData.cols) sheetData.cols = {};
            if (!sheetData.merges) sheetData.merges = [];
            
            // 确保merges数组中的项为字符串格式（如"A1:B2"）
            if (Array.isArray(sheetData.merges)) {
                if (sheetData.merges.length > 0) {
                    console.log(`转换工作表 "${sheetName}" 的 ${sheetData.merges.length} 个合并单元格`);
                }
                
                // 确保合并单元格是字符串格式
                const convertedMerges = sheetData.merges.map((merge: any) => {
                    // 检查是否已经是字符串格式
                    if (typeof merge === 'string' && /^[A-Z]+[0-9]+:[A-Z]+[0-9]+$/.test(merge)) {
                        return merge;
                    }
                    
                    // 如果是数组格式 [row, col, rowspan, colspan]
                    if (Array.isArray(merge) && merge.length === 4) {
                        const [startRow, startCol, rowspan, colspan] = merge;
                        const result = mergeRef(startRow, startCol, startRow + rowspan - 1, startCol + colspan - 1);
                        console.log(`转换数组格式合并单元格: [${startRow},${startCol},${rowspan},${colspan}] => ${result}`);
                        return result;
                    }
                    
                    // 如果是具有sri, sci, eri, eci属性的对象
                    if (typeof merge === 'object' && merge.sri !== undefined && merge.sci !== undefined && 
                        merge.eri !== undefined && merge.eci !== undefined) {
                        const result = mergeRef(merge.sri, merge.sci, merge.eri, merge.eci);
                        console.log(`转换对象格式合并单元格: {sri:${merge.sri},sci:${merge.sci},eri:${merge.eri},eci:${merge.eci}} => ${result}`);
                        return result;
                    }
                    
                    // 无法转换时返回null
                    console.warn('无法识别的合并单元格格式:', merge);
                    return null;
                }).filter(Boolean); // 过滤掉null值
                
                // 去重
                sheetData.merges = Array.from(new Set(convertedMerges));
                
                if (sheetData.merges.length > 0) {
                    console.log(`工作表 "${sheetName}" 合并单元格去重后: ${sheetData.merges.length}个`, sheetData.merges);
                }
            }
            
            // 确保工作表至少有一个单元格数据，防止XSpreadsheet解析错误
            if (Object.keys(sheetData.rows).length === 0) {
                sheetData.rows = {
                    0: {
                        cells: {
                            0: { text: `${sheetName}` }
                        }
                    }
                };
            }
            
            sheetsArray.push(sheetData);
            
            console.log(`转换工作表 "${sheetName}" 完成, 行数: ${Object.keys(sheetData.rows).length}, 样式数: ${sheetData.styles.length}`);
        });
        
        // 确保至少有一个工作表
        if (sheetsArray.length === 0) {
            console.warn('没有有效工作表数据，创建默认工作表');
            sheetsArray.push({
                name: '空白工作表',
                styles: [],
                rows: { 0: { cells: { 0: { text: '无数据' } } } },
                cols: {},
                merges: []
            });
        }
        
        console.log(`准备加载 ${sheetsArray.length} 个工作表:`, sheetsArray.map(s => s.name));

        console.log('sheetsArray', sheetsArray);
        
        try {
            // 先清空现有数据，确保干净的状态
            spreadsheet.loadData([]);
            
            // 最终检查每个工作表的数据结构
            sheetsArray.forEach((sheet, index) => {
                console.log(`检查工作表 ${index}:`, {
                    name: sheet.name,
                    rowCount: Object.keys(sheet.rows || {}).length,
                    colCount: Object.keys(sheet.cols || {}).length,
                    mergesCount: sheet.merges ? sheet.merges.length : 0,
                    stylesCount: sheet.styles ? sheet.styles.length : 0
                });
                
                // 样本输出：第一个合并单元格和第一行数据
                if (sheet.merges && sheet.merges.length > 0) {
                    console.log(`工作表 ${sheet.name} 第一个合并单元格:`, sheet.merges[0]);
                }
                
                const firstRowKey = Object.keys(sheet.rows || {})[0];
                if (firstRowKey) {
                    const firstRow = sheet.rows[firstRowKey];
                    console.log(`工作表 ${sheet.name} 第一行:`, {
                        cellCount: Object.keys(firstRow.cells || {}).length,
                        sample: Object.keys(firstRow.cells || {}).slice(0, 2).map(k => firstRow.cells[k])
                    });
                }
            });
            
            // 延迟加载，确保DOM已更新
            setTimeout(() => {
                try {
                    // 加载实际工作表数据
                    spreadsheet.loadData(sheetsArray);
                    console.log('数据成功加载到电子表格');
                    
                    // 强制重新渲染
                    setTimeout(() => {
                        try {
                            spreadsheet.reRender();
                            console.log('电子表格重新渲染完成');
                            
                            // 验证工作表是否正确加载
                            const data = spreadsheet.getData();
                            if (Array.isArray(data) && data.length > 0) {
                                console.log('验证成功: 已加载工作表:', data.map((s: any) => s.name).join(', '));
                                
                                // 检查合并单元格是否正确加载
                                data.forEach((sheet: any, index: number) => {
                                    if (sheet.merges && sheet.merges.length > 0) {
                                        console.log(`工作表 ${sheet.name} 合并单元格验证:`, {
                                            count: sheet.merges.length,
                                            sample: sheet.merges.slice(0, 3)
                                        });
                                    }
                                });
                            } else {
                                console.warn('验证警告: 工作表数据格式不正确', data);
                            }
                        } catch (err) {
                            console.error('重新渲染时出错:', err);
                        }
                    }, 200);
                } catch (err) {
                    console.error('加载工作表数据时出错:', err);
                    return false;
                }
            }, 100);
            
            return true;
        } catch (err) {
            console.error('设置工作表数据失败:', err);
            return false;
        }
    } catch (error) {
        console.error('加载多工作表数据失败:', error);
        return false;
    }
}

/**
 * 获取当前活动的工作表
 * @param spreadsheet 电子表格实例
 * @returns 当前活动的工作表数据
 */
export function getActiveSheet(spreadsheet: any): any {
    if (!spreadsheet) return null;
    
    try {
        // 尝试通过多种方式获取当前工作表
        const data = spreadsheet.getData();
        
        // 如果是数组，返回当前活动工作表
        if (Array.isArray(data)) {
            const activeIndex = spreadsheet.sheet.data().active;
            return data[activeIndex] || data[0];
        }
        
        // 如果是对象，直接返回
        return data;
    } catch (error) {
        console.error('获取活动工作表失败:', error);
        return null;
    }
}

/**
 * 创建工作表对象
 * @param name 工作表名称 
 * @param rowCount 行数
 * @param colCount 列数
 * @returns 工作表对象
 */
export function createWorksheetObject(name: string, rowCount: number = 100, colCount: number = 26): any {
    return {
        name,
        styles: [],
        rows: {},
        cols: {},
        merges: [],
        media: []
    };
} 