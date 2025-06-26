"""
测试远程URL下载、转换和预览
"""

import os
import sys
import argparse
import requests
import time
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 测试服务器URL
SERVER_URL = "http://localhost:5001"

# 远程文件URL
REMOTE_FILES = {
    "doc": "https://cdn.blog.berfen.com/test_files/test_doc.doc",
    "docx": "https://cdn.blog.berfen.com/test_files/test_docx.docx",
    "xls": "https://cdn.blog.berfen.com/test_files/test_xls.xls",
    "xlsx": "https://cdn.blog.berfen.com/test_files/test_xlsx.xlsx"
}

def check_server():
    """检查服务器是否运行"""
    try:
        response = requests.get(f"{SERVER_URL}/api/stats")
        if response.status_code == 200:
            print("✅ 服务器正在运行")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False

def test_url(url):
    """测试URL下载、转换和预览"""
    print(f"\n=== 开始测试URL: {url} ===")
    
    try:
        # 1. 下载和转换
        print("\n1. 测试URL下载和转换")
        response = requests.get(f"{SERVER_URL}/api/convert?url={url}")
        
        if response.status_code != 200:
            print(f"❌ URL处理失败: {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        if data["status"] != "success":
            print(f"❌ URL处理响应异常: {data}")
            return False
        
        task_id = data["task_id"]
        print(f"✅ URL处理任务已创建: {task_id}")
        
        # 2. 等待转换完成
        print("\n2. 等待转换完成")
        result_data = None
        
        for i in range(30):  # 最多等待30秒
            sys.stdout.write(f"\r等待转换完成: {i+1}秒")
            sys.stdout.flush()
            
            status_response = requests.get(f"{SERVER_URL}/api/convert/status/{task_id}")
            if status_response.status_code != 200:
                print(f"\n❌ 获取状态失败: {status_response.status_code}")
                print(status_response.text)
                return False
            
            status_data = status_response.json()
            if status_data["status"] == "failed":
                print(f"\n❌ 转换失败: {status_data}")
                return False
            
            if status_data["status"] == "success":
                print(f"\n✅ 转换成功")
                result_data = status_data
                break
            
            time.sleep(1)
        
        if not result_data:
            print("\n❌ 转换超时")
            return False
        
        # 3. 下载文件
        print("\n3. 测试文件下载")
        download_url = result_data.get("download_url")
        if not download_url:
            print("❌ 未获取到下载URL")
            return False
        
        download_response = requests.get(f"{SERVER_URL}{download_url}")
        if download_response.status_code != 200:
            print(f"❌ 文件下载失败: {download_response.status_code}")
            print(download_response.text)
            return False
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(download_response.content)
            temp_file_path = temp_file.name
        
        file_size = os.path.getsize(temp_file_path)
        print(f"✅ 文件下载成功，大小: {file_size} 字节")
        
        # 清理临时文件
        os.unlink(temp_file_path)
        
        # 4. 预览文件
        print("\n4. 测试文件预览")
        preview_url = result_data.get("preview_url")
        if not preview_url:
            print("❌ 未获取到预览URL")
            return False
        
        preview_response = requests.get(f"{SERVER_URL}{preview_url}")
        if preview_response.status_code != 200:
            print(f"❌ 文件预览失败: {preview_response.status_code}")
            print(preview_response.text)
            return False
        
        content_type = preview_response.headers.get("Content-Type", "")
        content_length = len(preview_response.content)
        
        print(f"✅ 文件预览成功")
        print(f"   - 内容类型: {content_type}")
        print(f"   - 内容大小: {content_length} 字节")
        
        print(f"\n=== URL测试通过: {url} ===")
        return True
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="测试远程URL文件预览")
    parser.add_argument(
        "file_type", 
        choices=["doc", "docx", "xls", "xlsx", "all"], 
        help="要测试的文件类型"
    )
    
    args = parser.parse_args()
    
    if not check_server():
        print("\n请先启动服务器：python -m file_preview.cli.main server")
        return
    
    if args.file_type == "all":
        for file_type, url in REMOTE_FILES.items():
            test_url(url)
    else:
        url = REMOTE_FILES.get(args.file_type)
        if not url:
            print(f"❌ 不支持的文件类型: {args.file_type}")
            return
        
        test_url(url)

if __name__ == "__main__":
    main() 