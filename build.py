#!/usr/bin/env python3
"""
编译脚本 - 用于将 file_preview 编译为二进制文件
自动检测当前环境并进行相应的编译
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def get_system_info():
    """获取系统信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    is_64bits = sys.maxsize > 2**32
    
    return {
        'system': system,
        'machine': machine,
        'is_64bits': is_64bits,
        'python_version': platform.python_version()
    }

def get_output_name():
    """根据系统生成输出文件名"""
    system_info = get_system_info()
    base_name = 'file-preview'
    
    if system_info['system'] == 'windows':
        return f"{base_name}.exe"
    return base_name

def get_pyinstaller_args():
    """获取 PyInstaller 参数"""
    output_name = get_output_name()
    args = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        '--onefile',  # 生成单个可执行文件
        '--name', output_name,
        '--add-data', 'config.yaml:.',  # 添加配置文件
        '--hidden-import', 'click',
        '--hidden-import', 'flask',
        '--hidden-import', 'requests',
        '--hidden-import', 'python-magic',
        '--hidden-import', 'PyYAML',
        '--hidden-import', 'file_preview',
        '--hidden-import', 'file_preview.cli',
        '--hidden-import', 'file_preview.core',
        '--hidden-import', 'file_preview.server',
        '--hidden-import', 'file_preview.utils',
        '--collect-all', 'file_preview',
    ]
    
    # 添加图标（如果存在）
    icon_path = Path('assets/icon.ico')
    if icon_path.exists():
        args.extend(['--icon', str(icon_path)])
    
    # 添加入口点脚本
    args.append('main.py')
    
    return args

def cleanup():
    """清理编译产生的临时文件"""
    paths_to_remove = ['build', 'dist', '*.spec']
    for path in paths_to_remove:
        if '*' in path:
            # 处理通配符
            for p in Path('.').glob(path):
                if p.is_file():
                    p.unlink()
        else:
            # 处理目录
            if os.path.exists(path):
                shutil.rmtree(path)

def build():
    """执行编译过程"""
    try:
        # 获取系统信息
        system_info = get_system_info()
        print(f"当前系统信息：")
        print(f"  操作系统: {system_info['system']}")
        print(f"  架构: {system_info['machine']}")
        print(f"  Python版本: {system_info['python_version']}")
        print(f"  {'64' if system_info['is_64bits'] else '32'}位系统")
        
        # 清理之前的编译文件
        print("\n清理之前的编译文件...")
        cleanup()
        
        # 获取编译参数
        args = get_pyinstaller_args()
        print("\n开始编译...")
        print(f"执行命令: {' '.join(args)}")
        
        # 执行编译
        result = subprocess.run(args, capture_output=True, text=True)
        
        if result.returncode == 0:
            output_path = os.path.join('dist', get_output_name())
            print(f"\n编译成功！")
            print(f"输出文件: {output_path}")
            print(f"文件大小: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
            
            # 创建发布目录结构
            dist_dir = Path('dist')
            for dir_name in ['cache', 'download', 'convert', 'log']:
                (dist_dir / dir_name).mkdir(exist_ok=True)
            
            # 复制配置文件
            shutil.copy2('config.yaml', dist_dir / 'config.yaml')
            
            print("\n创建了以下目录结构：")
            for path in sorted(dist_dir.rglob('*')):
                if path.is_file():
                    print(f"  文件: {path.relative_to(dist_dir)}")
                else:
                    print(f"  目录: {path.relative_to(dist_dir)}")
        else:
            print("\n编译失败！")
            print("错误信息：")
            print(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"\n编译过程中出现错误：{str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    build() 