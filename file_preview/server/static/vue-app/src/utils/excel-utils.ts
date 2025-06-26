/**
 * Excel文件处理工具
 * 提供Excel文件解析、数据转换等功能
 */

import * as XLSX from 'xlsx';
import * as ExcelJS from 'exceljs';

// 为Window声明Buffer属性
declare global {
  interface Window {
    Buffer: any;
    btoa: (data: string) => string;
    atob: (data: string) => string;
  }
}

// Buffer polyfill，解决浏览器环境中Buffer未定义的问题
if (typeof window !== 'undefined' && !window.Buffer) {
  window.Buffer = {
    from: (data: string, encoding: string) => {
      if (encoding === 'base64') {
        // 浏览器中的base64转换
        const binary = window.atob(data);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
          bytes[i] = binary.charCodeAt(i);
        }
        return bytes;
      }
      return null;
    }
  } as any;
}

/**
 * Excel单元格坐标类型
 */
export interface CellCoordinate {
  row: number;
  col: number;
}

/**
 * Excel单元格合并信息
 */
export interface MergeInfo {
  startRow: number;
  startCol: number;
  endRow: number;
  endCol: number;
}

/**
 * 单元格样式信息
 */
export interface CellStyle {
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
  fontSize?: number;
  color?: string;
  bgcolor?: string;
  align?: string;
  valign?: string;
  textwrap?: boolean;
  // 添加全量样式支持
  font?: {
    name?: string;
    family?: number;
    size?: number;
    bold?: boolean;
    italic?: boolean;
    underline?: boolean;
    color?: {
      theme?: number;
      tint?: number;
      rgb?: string;
      argb?: string;
    };
    charset?: number;
    scheme?: string;
  };
  fill?: {
    type?: string;
    pattern?: string;
    fgColor?: {
      theme?: number;
      tint?: number;
      rgb?: string;
      argb?: string;
      indexed?: number;
    };
    bgColor?: {
      theme?: number;
      tint?: number;
      rgb?: string;
      argb?: string;
      indexed?: number;
    };
  };
  alignment?: {
    horizontal?: string;
    vertical?: string;
    wrapText?: boolean;
    textRotation?: number;
    indent?: number;
  };
  border?: {
    top?: { style?: string; color?: string };
    bottom?: { style?: string; color?: string };
    left?: { style?: string; color?: string };
    right?: { style?: string; color?: string };
  };
  border2?: Record<string, any>; // 兼容样例中的border2属性
}

/**
 * 单元格数据
 */
export interface CellData {
  text: string;
  style?: CellStyle;
  image?: {
    src: string;
    width: number;
    height: number;
  };
  link?: string;
  merge?: [number, number]; // 添加合并单元格信息，格式为[rowspan, colspan]
}

export interface TableRow {
  cells: Record<string, CellData>; 
  height?: number;
}

export interface Sheet {
  name: string;
  rows: Record<number, TableRow>;
  cols?: Record<number, { width: number }>;
  rowCount: number;
  colCount: number;
  cells?: Record<string, CellData>;
  merges?: Array<{sri: number, sci: number, eri: number, eci: number}>;
}

export interface TableData extends Sheet {
  sheets?: Sheet[]; // 添加支持多个工作表
}

/**
 * 解析Excel文件
 * 支持xls和xlsx格式
 * @param data Excel文件数据
 */
export async function parseExcelFile(data: ArrayBuffer): Promise<{
  workbook: any;
  worksheets: string[];
  error?: string;
}> {
  try {
    console.log('开始使用ExcelJS解析Excel文件...');
    // 使用ExcelJS库解析
    const result = await parseExcelFileWithExcelJS(data);
    return result;
  } catch (excelJSError) {
    console.warn('ExcelJS解析失败，尝试使用XLSX解析:', excelJSError);
    
    try {
      // 如果ExcelJS解析失败，回退到XLSX库
      const workbook = XLSX.read(new Uint8Array(data), { 
        type: 'array',
        cellStyles: true,  // 启用单元格样式
        cellHTML: false,   // 不需要HTML
        cellFormula: true, // 解析公式
        cellNF: true,      // 解析数字格式
        cellDates: true,   // 解析日期
        cellText: true     // 获取格式化文本
      });
      
      if (!workbook || !workbook.SheetNames || workbook.SheetNames.length === 0) {
        throw new Error('无法读取工作表');
      }
      
      console.log('使用XLSX库成功解析Excel文件，工作表:', workbook.SheetNames);
      
      return {
        workbook,
        worksheets: workbook.SheetNames
      };
    } catch (xlsxError) {
      console.error('Excel解析失败:', xlsxError);
      throw new Error(`无法解析Excel文件: ${xlsxError instanceof Error ? xlsxError.message : '未知错误'}`);
    }
  }
}

/**
 * 使用ExcelJS解析Excel文件
 * @param data Excel文件数据
 */
export async function parseExcelFileWithExcelJS(data: ArrayBuffer): Promise<{
  workbook: ExcelJS.Workbook;
  worksheets: string[];
  error?: string;
}> {
  try {
    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.load(data);
    
    if (!workbook || !workbook.worksheets || workbook.worksheets.length === 0) {
      throw new Error('无法读取工作表');
    }
    
    const worksheetNames = workbook.worksheets.map(ws => ws.name);
    console.log('使用ExcelJS库成功解析Excel文件，工作表:', worksheetNames);
    
    return {
      workbook,
      worksheets: worksheetNames
    };
  } catch (error) {
    console.error('Excel解析失败:', error);
    throw new Error(`无法解析Excel文件: ${error instanceof Error ? error.message : '未知错误'}`);
  }
}

/**
 * 将索引转换为Excel列名 (0->A, 1->B, 25->Z, 26->AA)
 * @param index 列索引
 */
export function indexToColName(index: number): string {
  let colName = '';
  index++;
  while (index > 0) {
    const remainder = index % 26;
    if (remainder === 0) {
      colName = 'Z' + colName;
      index = Math.floor(index / 26) - 1;
    } else {
      colName = String.fromCharCode(remainder + 64) + colName;
      index = Math.floor(index / 26);
    }
  }
  return colName;
}

/**
 * 将列名转换为索引 (A->0, B->1, Z->25, AA->26)
 * @param colName 列名
 */
export function colNameToIndex(colName: string): number {
  let index = 0;
  for (let i = 0; i < colName.length; i++) {
    index = index * 26 + colName.charCodeAt(i) - 64;
  }
  return index - 1;
}

/**
 * 将ArrayBuffer转换为Base64字符串
 * @param buffer 要转换的ArrayBuffer
 */
export function arrayBufferToBase64(buffer: ArrayBuffer | Uint8Array | null): string {
  if (!buffer) return '';
  
  let binary = '';
  const bytes = new Uint8Array(buffer instanceof ArrayBuffer ? buffer : buffer);
  const len = bytes.byteLength;
  
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  
  return window.btoa(binary);
}

/**
 * RGB颜色转Hex
 * @param rgb RGB颜色对象
 */
export function rgbToHex(rgb: any): string | undefined {
  if (!rgb) return undefined;
  
  if (typeof rgb === 'string' && rgb.startsWith('#')) {
    return rgb;
  }
  
  if (rgb.r !== undefined && rgb.g !== undefined && rgb.b !== undefined) {
    const r = rgb.r.toString(16).padStart(2, '0');
    const g = rgb.g.toString(16).padStart(2, '0');
    const b = rgb.b.toString(16).padStart(2, '0');
    return `#${r}${g}${b}`;
  }
  
  return '#333333'; // 默认颜色
}

/**
 * 边框样式转换
 * @param excelStyle Excel边框样式
 */
export function getBorderStyle(excelStyle: string): string {
  if (!excelStyle) {
    return 'thin';
  }
  
  // Excel边框样式转换为表格支持的边框样式
  const styleMap: Record<string, string> = {
    'thin': 'thin',
    'medium': 'medium',
    'thick': 'thick',
    'dashed': 'dashed',
    'dotted': 'dotted',
    'double': 'double',
    'hair': 'thin'
  };
  
  return styleMap[excelStyle] || 'thin';
}

/**
 * 从XLSX工作表提取数据
 * @param worksheet XLSX工作表
 * @param sheetName 工作表名称
 */
export function extractXLSXWorksheetData(worksheet: XLSX.WorkSheet, sheetName: string): TableData {
  const cells: Record<string, CellData> = {};
  const tableRows: Record<number, TableRow> = {};
  const rows: Record<number, {height: number}> = {};
  const cols: Record<number, {width: number}> = {};
  const merges: Array<{sri: number, sci: number, eri: number, eci: number}> = [];
  
  // 获取工作表范围
  const range = XLSX.utils.decode_range(worksheet['!ref'] || 'A1:J10');
  const rowCount = range.e.r - range.s.r + 1;
  const colCount = range.e.c - range.s.c + 1;
  
  // 处理合并单元格
  if (worksheet['!merges'] && worksheet['!merges'].length > 0) {
    worksheet['!merges'].forEach(merge => {
      merges.push({
        sri: merge.s.r,
        sci: merge.s.c,
        eri: merge.e.r,
        eci: merge.e.c
      });
    });
  }
  
  // 处理行高
  if (worksheet['!rows']) {
    Object.entries(worksheet['!rows']).forEach(([rowIdx, rowData]: [string, any]) => {
      if (rowData && rowData.hpt) {
        const rowIndex = parseInt(rowIdx);
        rows[rowIndex] = { height: rowData.hpt };
      }
    });
  }
  
  // 处理列宽
  if (worksheet['!cols']) {
    Object.entries(worksheet['!cols']).forEach(([colIdx, colData]: [string, any]) => {
      if (colData && colData.width) {
        const colIndex = parseInt(colIdx);
        cols[colIndex] = { width: colData.width };
      }
    });
  }
  
  // 处理单元格数据
  Object.entries(worksheet).forEach(([cellRef, cell]: [string, any]) => {
    // 跳过非单元格属性
    if (cellRef.startsWith('!')) return;
    
    const cellAddress = XLSX.utils.decode_cell(cellRef);
    const rowIndex = cellAddress.r;
    const colIndex = cellAddress.c;
    
    const cellData: CellData = { text: '' };
    
    // 处理单元格值
    if (cell.v !== undefined) {
      if (cell.w !== undefined) {
        // 格式化的值
        cellData.text = cell.w;
      } else {
        // 原始值
        cellData.text = String(cell.v);
      }
    }
    
    // 处理超链接
    if (cell.l && cell.l.Target) {
      cellData.link = cell.l.Target;
    }
    
    // 处理单元格样式
    if (cell.s) {
      // 创建样式对象
      const style: CellStyle = {};
      
      // 处理字体样式
      if (cell.s.font) {
        if (cell.s.font.bold) style.bold = true;
        if (cell.s.font.italic) style.italic = true;
        if (cell.s.font.underline) style.underline = true;
        if (cell.s.font.sz) style.fontSize = cell.s.font.sz;
        
        // 处理颜色
        if (cell.s.font.color) {
          if (cell.s.font.color.rgb) {
            style.color = `#${cell.s.font.color.rgb}`;
          } else if (cell.s.font.color.theme !== undefined) {
            // 主题颜色处理
            const themeColor = getThemeColor(cell.s.font.color.theme, cell.s.font.color.tint);
            if (themeColor) style.color = themeColor;
          }
        }
      }
      
      // 处理背景色
      if (cell.s.fill) {
        if (cell.s.fill.fgColor && cell.s.fill.fgColor.rgb) {
          style.bgcolor = `#${cell.s.fill.fgColor.rgb}`;
        } else if (cell.s.fill.fgColor && cell.s.fill.fgColor.theme !== undefined) {
          // 主题背景色处理
          const themeBgColor = getThemeColor(cell.s.fill.fgColor.theme, cell.s.fill.fgColor.tint);
          if (themeBgColor) style.bgcolor = themeBgColor;
        }
      }
      
      // 处理对齐
      if (cell.s.alignment) {
        if (cell.s.alignment.horizontal) style.align = cell.s.alignment.horizontal;
        if (cell.s.alignment.vertical) style.valign = cell.s.alignment.vertical;
        if (cell.s.alignment.wrapText) style.textwrap = true;
      }
      
      // 处理边框
      if (cell.s.border) {
        const border: Record<string, { style?: string; color?: string }> = {};
        
        ['top', 'bottom', 'left', 'right'].forEach(direction => {
          const borderDir = cell.s.border[direction];
          if (borderDir && borderDir.style) {
            border[direction] = {
              style: getBorderStyle(borderDir.style)
            };
            
            // 处理边框颜色
            if (borderDir.color) {
              if (borderDir.color.rgb) {
                border[direction].color = `#${borderDir.color.rgb}`;
              } else if (borderDir.color.theme !== undefined) {
                const borderColor = getThemeColor(borderDir.color.theme, borderDir.color.tint);
                if (borderColor) border[direction].color = borderColor;
              }
            }
          }
        });
        
        if (Object.keys(border).length > 0) {
          style.border = border;
        }
      }
      
      // 只有当样式有实际内容时才添加
      if (Object.keys(style).length > 0) {
        cellData.style = style;
      }
    }
    
    // 存储单元格数据
    cells[`${rowIndex}_${colIndex}`] = cellData;
    
    // 按行组织单元格数据，用于满足TableRow接口要求
    if (!tableRows[rowIndex]) {
      tableRows[rowIndex] = { cells: {} };
    }
    tableRows[rowIndex].cells[colIndex.toString()] = cellData;
  });
  
  // 应用行高
  Object.entries(rows).forEach(([rowIndex, rowData]) => {
    const rowIdx = parseInt(rowIndex);
    if (tableRows[rowIdx]) {
      tableRows[rowIdx].height = rowData.height;
    }
  });
  
  return {
    name: sheetName,
    rows: tableRows,
    cols,
    cells,
    merges,
    rowCount,
    colCount
  };
}

/**
 * 获取主题颜色
 * Excel主题颜色转换为HEX
 * @param theme 主题索引
 * @param tint 色调调整值
 */
function getThemeColor(theme: number, tint?: number): string | undefined {
  // Excel主题颜色映射 (简化版)
  const themeColors = [
    '#FFFFFF', // 0: 背景
    '#000000', // 1: 文本
    '#E7E6E6', // 2: 背景2
    '#44546A', // 3: 文本2
    '#4472C4', // 4: 强调1
    '#ED7D31', // 5: 强调2
    '#A5A5A5', // 6: 强调3
    '#FFC000', // 7: 强调4
    '#5B9BD5', // 8: 强调5
    '#70AD47', // 9: 强调6
    '#0563C1', // 10: 超链接
    '#954F72'  // 11: 已访问超链接
  ];
  
  if (theme === undefined || theme < 0 || theme >= themeColors.length) {
    return undefined;
  }
  
  let color = themeColors[theme];
  
  // 应用色调
  if (tint !== undefined && tint !== 0) {
    // 将颜色从HEX转为RGB
    const r = parseInt(color.slice(1, 3), 16);
    const g = parseInt(color.slice(3, 5), 16);
    const b = parseInt(color.slice(5, 7), 16);
    
    // 应用色调变换
    const adjustedColor = applyTint([r, g, b], tint);
    
    // 转回HEX
    color = `#${adjustedColor.map(c => Math.round(c).toString(16).padStart(2, '0')).join('')}`;
  }
  
  return color;
}

/**
 * 应用色调到RGB颜色
 * @param rgb RGB颜色数组 [r, g, b]
 * @param tint 色调值 (-1 到 1)
 */
function applyTint(rgb: number[], tint: number): number[] {
  // Excel色调算法
  if (tint < 0) {
    // 变暗
    return rgb.map(c => c * (1 + tint));
  } else {
    // 变亮
    return rgb.map(c => c * (1 - tint) + (255 - 255 * (1 - tint)));
  }
}

/**
 * 解析 Excel 工作表数据
 * @param rowData 行数据，通常为2D数组
 * @param options 选项
 * @returns TableData 格式化后的表格数据
 */
export function parseExcelSheetData(
  rowData: any[][] = [], 
  options: { 
    maxRows?: number; 
    maxCols?: number;
    skipEmptyRows?: boolean; 
    trimValues?: boolean;
  } = {}
): TableData {
  // 设置默认选项
  const { 
    maxRows = 1000, 
    maxCols = 100,
    skipEmptyRows = true,
    trimValues = true
  } = options;

  // 初始化表格数据结构
  const cells: Record<string, CellData> = {};
  const tableRows: Record<number, TableRow> = {};
  
  // 处理空数据情况
  if (!rowData || !Array.isArray(rowData) || rowData.length === 0) {
    console.warn('parseExcelSheetData: 没有数据或数据格式不正确');
    return {
      name: 'Sheet1',
      rows: {},
      cells: {},
      rowCount: 0,
      colCount: 0
    };
  }

  try {
    // 计算有效行数和列数
    let rowCount = Math.min(rowData.length, maxRows);
    let colCount = 0;

    // 遍历所有行，找出最大列数
    for (let i = 0; i < rowCount; i++) {
      const row = rowData[i];
      if (Array.isArray(row)) {
        colCount = Math.max(colCount, Math.min(row.length, maxCols));
      }
    }

    // 填充表格数据
    let validRowIndex = 0;
    for (let i = 0; i < rowCount; i++) {
      const row = rowData[i];
      
      // 跳过非数组行
      if (!Array.isArray(row)) {
        continue;
      }

      // 检查是否跳过空行
      if (skipEmptyRows) {
        const hasNonEmptyCell = row.some(cell => 
          cell !== null && 
          cell !== undefined && 
          (!trimValues || String(cell).trim() !== '')
        );
        
        if (!hasNonEmptyCell) {
          continue;
        }
      }

      // 创建行对象
      const rowObj: TableRow = {
        cells: {}
      };

      // 填充单元格数据
      for (let j = 0; j < Math.min(row.length, maxCols); j++) {
        let cellValue = row[j];
        
        // 处理单元格值
        if (cellValue !== null && cellValue !== undefined) {
          if (trimValues && typeof cellValue === 'string') {
            cellValue = cellValue.trim();
          }
          
          // 只添加非空单元格
          if (!trimValues || cellValue !== '') {
            const cellData: CellData = { text: String(cellValue) };
            rowObj.cells[j.toString()] = cellData;
            cells[`${validRowIndex}_${j}`] = cellData;
          }
        }
      }

      // 只添加有内容的行
      if (Object.keys(rowObj.cells).length > 0) {
        tableRows[validRowIndex] = rowObj;
        validRowIndex++;
      }
    }

    // 更新最终的行数和列数
    return {
      name: 'Sheet1',
      rows: tableRows,
      cells,
      rowCount: validRowIndex,
      colCount
    };
  } catch (error) {
    console.error('解析Excel工作表数据时出错:', error);
    return {
      name: 'Sheet1',
      rows: {},
      cells: {},
      rowCount: 0,
      colCount: 0
    };
  }
}

/**
 * 创建一个多工作表数据对象
 * @param sheetDataItems 工作表数据项数组
 * @returns 带有多个工作表的TableData对象
 */
export function createMultiSheetData(sheetDataItems: Sheet[]): TableData {
  // 默认使用第一个工作表的数据作为主数据
  const firstSheet = sheetDataItems[0] || { 
    name: 'Sheet1',
    rows: {},
    rowCount: 0,
    colCount: 0
  };

  return {
    ...firstSheet,
    sheets: sheetDataItems
  };
}

// 添加类型定义
export interface ExtractExcelOptions {
  includeEmpty?: boolean;
  maxRows?: number;
  maxCols?: number;
}

export interface ParsedExcelData {
  cells: Record<string, any>;
  rows: number;
  cols: number;
  merges: Array<{ r: number; c: number; rs: number; cs: number }>;
}

/**
 * 从 ExcelJS 的 Worksheet 中提取数据
 * @param worksheet ExcelJS 的 Worksheet 对象
 * @param sheetName 工作表名称
 * @returns 提取的表格数据，符合 TableData 接口
 */
export function extractExcelJSWorksheetData(worksheet: ExcelJS.Worksheet, sheetName: string): TableData {
  // 初始化数据结构
  const cells: Record<string, CellData> = {};
  const tableRows: Record<number, TableRow> = {};
  const cols: Record<number, { width: number }> = {};
  const merges: Array<{sri: number, sci: number, eri: number, eci: number}> = [];
  
  // 获取工作表范围
  const rowCount = worksheet.rowCount || 0;
  const colCount = worksheet.columnCount || 0;
  
  console.log(`提取工作表 ${sheetName} 数据，行数: ${rowCount}, 列数: ${colCount}`);
  
  // 收集合并单元格信息
  try {
    
    // 尝试多种方法获取合并单元格信息
    const mergeCellsFound: { startRow: number; startCol: number; endRow: number; endCol: number }[] = [];
    
    // 方法1: 尝试使用model属性
    if ((worksheet as any).model && (worksheet as any).model.mergeCells) {
      try {
        const modelMergeCells = (worksheet as any).model.mergeCells;
        console.log('找到 model.mergeCells', modelMergeCells);
        
        if (Array.isArray(modelMergeCells)) {
          modelMergeCells.forEach((mergeCell: any) => {
            if (mergeCell && mergeCell.tl && mergeCell.br) {
              const topLeft = mergeCell.tl;
              const bottomRight = mergeCell.br;
              
              mergeCellsFound.push({
                startRow: topLeft.row,
                startCol: topLeft.col,
                endRow: bottomRight.row,
                endCol: bottomRight.col
              });
            }
          });
        } else if (typeof modelMergeCells === 'object') {
          Object.keys(modelMergeCells).forEach(range => {
            const [start, end] = range.split(':');
            if (start && end) {
              const startAddr = getAddressInfo(start);
              const endAddr = getAddressInfo(end);
              
              if (startAddr && endAddr) {
                mergeCellsFound.push({
                  startRow: startAddr.row,
                  startCol: startAddr.col,
                  endRow: endAddr.row,
                  endCol: endAddr.col
                });
              }
            }
          });
        }
      } catch (e) {
        console.error('使用model.mergeCells获取合并单元格失败:', e);
      }
    }
    
    // 方法2: 直接尝试获取worksheet.mergeCells
    if (worksheet.mergeCells && typeof worksheet.mergeCells === 'object') {
      try {
        if (!Array.isArray(worksheet.mergeCells)) {
          Object.keys(worksheet.mergeCells).forEach(range => {
            if (range && range.includes(':')) {
              const [start, end] = range.split(':');
              if (start && end) {
                const startAddr = getAddressInfo(start);
                const endAddr = getAddressInfo(end);
                
                if (startAddr && endAddr) {
                  mergeCellsFound.push({
                    startRow: startAddr.row,
                    startCol: startAddr.col,
                    endRow: endAddr.row,
                    endCol: endAddr.col
                  });
                }
              }
            }
          });
        } else {
          // 如果是数组，尝试直接使用
          (worksheet.mergeCells as any).forEach((range: string) => {
            if (typeof range === 'string' && range.includes(':')) {
              const [start, end] = range.split(':');
              if (start && end) {
                const startAddr = getAddressInfo(start);
                const endAddr = getAddressInfo(end);
                
                if (startAddr && endAddr) {
                  mergeCellsFound.push({
                    startRow: startAddr.row,
                    startCol: startAddr.col,
                    endRow: endAddr.row,
                    endCol: endAddr.col
                  });
                }
              }
            }
          });
        }
      } catch (e) {
        console.error('直接访问mergeCells获取合并单元格失败:', e);
      }
    }
    
    // 方法3: 尝试使用_merges属性
    if ((worksheet as any)._merges) {
      try {
        const _merges = (worksheet as any)._merges;
        Object.keys(_merges).forEach(key => {
          const merge = _merges[key];
          if (merge && merge.top && merge.left && merge.bottom && merge.right) {
            mergeCellsFound.push({
              startRow: merge.top,
              startCol: merge.left, 
              endRow: merge.bottom,
              endCol: merge.right
            });
          }
        });
      } catch (e) {
        console.error('使用_merges获取合并单元格失败:', e);
      }
    }
    
    // 去重并转换为TableData需要的格式
    const mergeMap = new Map();
    mergeCellsFound.forEach(merge => {
      // 从1开始 转为 从0开始
      const sri = merge.startRow - 1;
      const sci = merge.startCol - 1;
      const eri = merge.endRow - 1;
      const eci = merge.endCol - 1;
      
      // 忽略无效的合并区域
      if (sri < 0 || sci < 0 || eri < sri || eci < sci) {
        return;
      }
      
      const key = `${sri}_${sci}_${eri}_${eci}`;
      if (!mergeMap.has(key)) {
        merges.push({ sri, sci, eri, eci });
        mergeMap.set(key, true);
      }
    });
    
    console.log(`找到 ${merges.length} 个有效合并单元格区域`);
  } catch (e) {
    console.error('处理合并单元格时出错:', e);
  }
  
  // 处理列宽
  if (worksheet.columns && Array.isArray(worksheet.columns)) {
    worksheet.columns.forEach((column, index) => {
      if (column && column.width) {
        cols[index] = { width: column.width };
      }
    });
  }
  
  // 处理行和单元格
  try {
    // 首先收集所有有样式的单元格，包括空单元格
    const styledCells: Record<string, CellStyle> = {};
    
    // 遍历所有单元格，包括空单元格
    worksheet.eachRow({ includeEmpty: true }, (row, rowIndex) => {
      row.eachCell({ includeEmpty: true }, (cell, colIndex) => {
        // 检查单元格是否有样式
        const rowIdx = rowIndex - 1;
        const colIdx = colIndex - 1;
        const cellKey = `${rowIdx}_${colIdx}`;
        
        // 检查单元格样式，不要仅依赖cell.style属性
        const style = getCellStyle(cell);
        if (Object.keys(style).length > 0) {
          styledCells[cellKey] = style;
          console.log(`发现带样式的单元格: ${cellKey}`, style);
        }
      });
    });
    
    console.log(`发现带样式的单元格总数: ${Object.keys(styledCells).length}`);
    
    // 正常处理非空单元格
    worksheet.eachRow({ includeEmpty: false }, (row, rowIndex) => {
      // 创建行对象
      const tableRow: TableRow = {
        cells: {}
      };
      
      // 设置行高 - 保留原始pt单位，转换将在spreadsheet-utils中进行
      if (row.height) {
        tableRow.height = row.height;
      }
      
      // 处理行中的每个单元格
      row.eachCell({ includeEmpty: false }, (cell, colIndex) => {
        const rowIdx = rowIndex - 1;  // 转换为0索引
        const colIdx = colIndex - 1;  // 转换为0索引
        const cellKey = `${rowIdx}_${colIdx}`;
        
        // 创建单元格数据
        const cellData: CellData = {
          text: getCellValue(cell)
        };
        
        // 处理单元格样式
        const style = getCellStyle(cell);
        if (Object.keys(style).length > 0) {
          cellData.style = style;
          // 从收集的样式中移除，因为已经处理过了
          delete styledCells[cellKey];
        }
        
        // 处理超链接
        if (cell.hyperlink) {
          if (typeof cell.hyperlink === 'string') {
            cellData.link = cell.hyperlink;
          } else if (cell.hyperlink && typeof cell.hyperlink === 'object') {
            // hyperlink 可能是对象，安全访问其属性
            const hyperlinkObj = cell.hyperlink as any;
            cellData.link = hyperlinkObj.target || hyperlinkObj.address || hyperlinkObj.toString() || '';
          }
        }
        
        // 检查是否是合并单元格
        const mergeInfo = findMergeInfo(rowIdx, colIdx, merges);
        if (mergeInfo && rowIdx === mergeInfo.sri && colIdx === mergeInfo.sci) {
          // 只在左上角单元格设置合并信息
          const rowSpan = mergeInfo.eri - mergeInfo.sri + 1;
          const colSpan = mergeInfo.eci - mergeInfo.sci + 1;
          cellData.merge = [rowSpan, colSpan];
        }
        
        // 保存单元格数据
        tableRow.cells[colIdx.toString()] = cellData;
        cells[cellKey] = cellData;
      });
      
      // 添加行
      tableRows[rowIndex - 1] = tableRow;
    });
    
    // 处理仅有样式但无内容的单元格
    console.log(`处理剩余有样式但无内容的单元格数量: ${Object.keys(styledCells).length}`);
    Object.entries(styledCells).forEach(([cellKey, style]) => {
      const [rowIdx, colIdx] = cellKey.split('_').map(Number);
      
      // 确保行对象存在
      if (!tableRows[rowIdx]) {
        tableRows[rowIdx] = { cells: {} };
      }
      
      // 创建空单元格数据，但带有样式
      const cellData: CellData = {
        text: '', // 空文本
        style: style // 应用保存的样式
      };
      
      // 检查是否是合并单元格
      const mergeInfo = findMergeInfo(rowIdx, colIdx, merges);
      if (mergeInfo && rowIdx === mergeInfo.sri && colIdx === mergeInfo.sci) {
        // 只在左上角单元格设置合并信息
        const rowSpan = mergeInfo.eri - mergeInfo.sri + 1;
        const colSpan = mergeInfo.eci - mergeInfo.sci + 1;
        cellData.merge = [rowSpan, colSpan];
      }
      
      // 保存单元格数据
      tableRows[rowIdx].cells[colIdx.toString()] = cellData;
      cells[cellKey] = cellData;
      
      console.log(`添加空单元格 [${rowIdx},${colIdx}] 带样式:`, style);
    });
  } catch (e) {
    console.error('处理行和单元格时出错:', e);
  }
  
  // 辅助函数：从单元格引用(如 A1)中提取行列信息
  function getAddressInfo(address: string): { row: number; col: number } | null {
    try {
      const cell = worksheet.getCell(address);
      return {
        row: typeof cell.row === 'string' ? parseInt(cell.row, 10) : cell.row,
        col: typeof cell.col === 'string' ? parseInt(cell.col, 10) : cell.col
      };
    } catch (e) {
      // 如果无法通过worksheet.getCell获取，尝试手动解析
      const match = address.match(/^([A-Z]+)(\d+)$/);
      if (!match) return null;
      
      const [, colStr, rowStr] = match;
      const row = parseInt(rowStr, 10);
      
      // 将列引用（如'A', 'BC'）转换为数字
      const colChars = colStr.split('');
      let col = 0;
      for (let i = 0; i < colChars.length; i++) {
        col = col * 26 + (colChars[i].charCodeAt(0) - 64); // 'A'的ASCII码是65
      }
      
      return { row, col };
    }
  }
  
  return {
    name: sheetName,
    rows: tableRows,
    cols,
    cells,
    merges,
    rowCount,
    colCount
  };
}

/**
 * 获取单元格值
 */
function getCellValue(cell: ExcelJS.Cell): string {
  if (cell.value === null || cell.value === undefined) {
    return '';
  }
  
  // 如果有格式化的文本，优先使用
  if (cell.text) {
    return cell.text;
  }
  
  if (cell.value instanceof Date) {
    // 对日期类型特殊处理
    return cell.value.toISOString().split('T')[0]; // 简化日期格式为YYYY-MM-DD
  } else if (typeof cell.value === 'object' && cell.value) {
    // 富文本处理
    try {
      // 安全地访问富文本内容
      const richTextObj = cell.value as any;
      
      // 尝试不同的属性名和结构
      if (richTextObj.richText && Array.isArray(richTextObj.richText)) {
        return richTextObj.richText.map((t: any) => t.text || '').join('');
      } else if (richTextObj.text) {
        return richTextObj.text;
      } else if (Array.isArray(richTextObj)) {
        return richTextObj.map((t: any) => t.text || '').join('');
      }
      
      // 如果无法解析，转为字符串
      return String(cell.value);
    } catch (e) {
      return String(cell.value);
    }
  } else {
    // 其他类型值转为字符串
    return String(cell.value);
  }
}

/**
 * 获取单元格样式
 */
function getCellStyle(cell: ExcelJS.Cell): CellStyle {
  const style: CellStyle = {};
  
  if (!cell.style) {
    return style;
  }
  
  // 添加原始字体对象
  if (cell.style.font) {
    // 先初始化font对象
    style.font = {
      color: {}
    } as CellStyle['font'];
    
    const font = cell.style.font;
    // 因为上面已经初始化了style.font，所以这里style.font一定存在
    if (font.name) style.font!.name = font.name;
    if (font.size) style.font!.size = font.size;
    if (font.family) style.font!.family = font.family;
    if (font.scheme) style.font!.scheme = font.scheme as string;
    if (font.charset) style.font!.charset = font.charset;
    if (typeof font.bold === 'boolean') style.font!.bold = font.bold;
    if (typeof font.italic === 'boolean') style.font!.italic = font.italic;
    
    // 处理下划线，ExcelJS中可能是string类型
    if (font.underline) {
      style.font!.underline = typeof font.underline === 'boolean' 
        ? font.underline 
        : true; // 如果是字符串值如"single"，则转为true
    }
    
    // 常用字体属性单独提取
    if (font.bold) style.bold = true;
    if (font.italic) style.italic = true;
    if (font.underline) style.underline = true;
    if (font.size) style.fontSize = font.size;
    
    // 字体颜色
    if (font.color) {
      // 提取格式化的颜色
      if (typeof font.color === 'string') {
        style.color = font.color;
      } else if (font.color.argb) {
        style.color = `#${font.color.argb.substring(2)}`;
        if (style.font!.color) {
          style.font!.color.argb = font.color.argb;
        }
      } else if (font.color.theme !== undefined) {
        // 主题颜色处理
        if (font.color.theme === 0) {
          style.color = '#FFFFFF'; // 主题0通常是白色
        } else if (font.color.theme === 1) {
          style.color = '#000000'; // 主题1通常是黑色
        }
        
        if (style.font!.color) {
          style.font!.color.theme = font.color.theme;
        }
      }
      
      // 复制其他颜色属性
      if (typeof font.color !== 'string' && style.font!.color) {
        if ((font.color as any).tint !== undefined) {
          style.font!.color.tint = (font.color as any).tint;
        }
        
        if ((font.color as any).rgb) {
          (style.font!.color as any).rgb = (font.color as any).rgb;
        }
      }
    }
  }
  
  // 初始化填充/背景
  if (cell.style.fill) {
    style.fill = {} as CellStyle['fill'];
    
    // 填充/背景色
    if (cell.style.fill.type === 'pattern') {
      const fill = cell.style.fill as ExcelJS.FillPattern;
      style.fill!.type = fill.type;
      style.fill!.pattern = fill.pattern;

      // 处理前景色
      if (fill.fgColor) {
        style.fill!.fgColor = {} as any;
        
        // 提取格式化的背景色
        if (typeof fill.fgColor === 'string') {
          style.bgcolor = fill.fgColor;
        } else if (fill.fgColor.argb) {
          style.bgcolor = `#${fill.fgColor.argb.substring(2)}`;
          style.fill!.fgColor!.argb = fill.fgColor.argb;
        } else if (fill.fgColor.theme !== undefined) {
          // 主题背景色处理
          if (fill.fgColor.theme === 0) {
            style.bgcolor = '#FFFFFF'; // 主题0通常是白色
          } else if (fill.fgColor.theme === 1) {
            style.bgcolor = '#000000'; // 主题1通常是黑色
          }
          
          style.fill!.fgColor!.theme = fill.fgColor.theme;
        }
        
        // 复制其他颜色属性
        if (typeof fill.fgColor !== 'string') {
          if ((fill.fgColor as any).tint !== undefined) {
            (style.fill!.fgColor as any).tint = (fill.fgColor as any).tint;
          }
          
          if ((fill.fgColor as any).rgb) {
            (style.fill!.fgColor as any).rgb = (fill.fgColor as any).rgb;
          }
        }
      }
      
      // 处理背景色
      if (fill.bgColor) {
        style.fill!.bgColor = {} as any;
        
        // 提取格式化的背景色
        if (typeof fill.bgColor === 'string') {
          style.bgcolor = fill.bgColor;
        } else if (fill.bgColor.argb) {
          style.bgcolor = `#${fill.bgColor.argb.substring(2)}`;
          style.fill!.bgColor!.argb = fill.bgColor.argb;
        } else if (fill.bgColor.theme !== undefined) {
          // 主题背景色处理
          if (fill.bgColor.theme === 0) {
            style.bgcolor = '#FFFFFF'; // 主题0通常是白色
          } else if (fill.bgColor.theme === 1) {
            style.bgcolor = '#000000'; // 主题1通常是黑色
          }
          
          style.fill!.bgColor!.theme = fill.bgColor.theme;
        }
        
        // 如果没有前景色，但有背景色，也设置bgcolor
        if (!style.bgcolor && fill.bgColor) {
          if (typeof fill.bgColor === 'string') {
            style.bgcolor = fill.bgColor;
          } else if (fill.bgColor.argb) {
            style.bgcolor = `#${fill.bgColor.argb.substring(2)}`;
          }
        }
      }
    } else if (cell.style.fill.type === 'gradient') {
      // 处理渐变填充
      const gradientFill = cell.style.fill as any;
      if (gradientFill.start && gradientFill.start.argb) {
        style.bgcolor = `#${gradientFill.start.argb.substring(2)}`;
      }
    }
  }
  
  // 对齐方式
  if (cell.style.alignment) {
    // 初始化alignment对象
    style.alignment = {} as CellStyle['alignment'];
    
    const alignment = cell.style.alignment;
    
    // 使用安全的类型处理，通过类型断言来解决类型不匹配问题
    if (alignment.horizontal) {
      style.alignment!.horizontal = alignment.horizontal;
      // 同时设置简写属性
      style.align = alignment.horizontal;
    }
    
    // 使用类型断言处理vertical属性
    if ((alignment as any).vertical) {
      const verticalValue = (alignment as any).vertical;
      style.alignment!.vertical = verticalValue as string;
      // 同时设置简写属性
      style.valign = verticalValue as string;
    }
    
    if (alignment.wrapText !== undefined) {
      style.alignment!.wrapText = alignment.wrapText;
      // 设置textwrap简写属性
      if (alignment.wrapText) {
        style.textwrap = true;
      }
    }
    
    // 使用类型断言确保textRotation的类型正确
    if (alignment.textRotation !== undefined) {
      const rotation = alignment.textRotation;
      // 只处理数字类型的textRotation
      if (typeof rotation === 'number') {
        style.alignment!.textRotation = rotation;
      }
    }
    
    // 处理indent属性
    if (alignment.indent !== undefined) {
      style.alignment!.indent = alignment.indent;
    }
  }
  
  // 边框样式
  if (cell.style.border) {
    const border: Record<string, { style?: string; color?: string }> = {};
    
    ['top', 'bottom', 'left', 'right'].forEach(direction => {
      const borderDir = cell.style.border?.[direction as keyof ExcelJS.Borders];
      if (borderDir && borderDir.style) {
        border[direction] = {
          style: getBorderStyle(borderDir.style)
        };
        
        // 边框颜色
        if (borderDir.color) {
          if (typeof borderDir.color === 'string') {
            border[direction].color = borderDir.color;
          } else if (borderDir.color.argb) {
            border[direction].color = `#${borderDir.color.argb.substring(2)}`;
          }
        }
      }
    });
    
    if (Object.keys(border).length > 0) {
      style.border = border;
      // 添加border2保持兼容性
      style.border2 = {};
    }
  }
  
  return style;
}

/**
 * 查找单元格所在的合并区域
 */
function findMergeInfo(
  rowIndex: number, 
  colIndex: number, 
  merges: Array<{sri: number, sci: number, eri: number, eci: number}>
): {sri: number, sci: number, eri: number, eci: number} | undefined {
  return merges.find(merge => 
    rowIndex >= merge.sri && rowIndex <= merge.eri && 
    colIndex >= merge.sci && colIndex <= merge.eci
  );
} 