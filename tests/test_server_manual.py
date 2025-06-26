"""
手动测试服务器模块的功能
"""

import os
import requests
import time
from pathlib import Path
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 测试服务器URL
SERVER_URL = "http://localhost:5001"

# 测试文件路径
TEST_FILES_DIR = Path("test_files")
TEST_DOC = TEST_FILES_DIR / "test_doc.doc"
TEST_DOCX = TEST_FILES_DIR / "test_docx.docx"
TEST_XLS = TEST_FILES_DIR / "test_xls.xls"
TEST_XLSX = TEST_FILES_DIR / "test_xlsx.xlsx"

# 远程文件URL
REMOTE_FILES = {
    "DOC": "https://cdn.blog.berfen.com/test_files/test_doc.doc",
    "DOCX": "https://cdn.blog.berfen.com/test_files/test_docx.docx",
    "XLS": "https://cdn.blog.berfen.com/test_files/test_xls.xls",
    "XLSX": "https://cdn.blog.berfen.com/test_files/test_xlsx.xlsx"
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

def test_file_upload(file_path):
    """测试文件上传功能"""
    print(f"\n正在测试文件上传: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ 测试文件不存在: {file_path}")
        return None
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{SERVER_URL}/api/convert", files=files)
        
        if response.status_code != 200:
            print(f"❌ 文件上传失败: {response.status_code}")
            print(response.text)
            return None
        
        data = response.json()
        
        if data["status"] != "success":
            print(f"❌ 文件上传响应异常: {data}")
            return None
        
        task_id = data["task_id"]
        print(f"✅ 文件已上传，任务ID: {task_id}")
        return task_id
    
    except Exception as e:
        print(f"❌ 文件上传异常: {e}")
        return None

def test_url_download(url):
    """测试URL下载功能"""
    print(f"\n正在测试URL下载和转换: {url}")
    
    try:
        response = requests.get(f"{SERVER_URL}/api/convert?url={url}")
        
        if response.status_code != 200:
            print(f"❌ URL下载失败: {response.status_code}")
            print(response.text)
            return None
        
        data = response.json()
        
        if data["status"] != "success":
            print(f"❌ URL下载响应异常: {data}")
            return None
        
        task_id = data["task_id"]
        print(f"✅ URL已处理，任务ID: {task_id}")
        return task_id
    
    except Exception as e:
        print(f"❌ URL下载异常: {e}")
        return None

def check_conversion_status(task_id):
    """检查转换状态"""
    print(f"\n正在检查转换状态: {task_id}")
    
    try:
        # 等待转换完成
        for i in range(30):  # 最多等待30秒
            sys.stdout.write(f"\r等待转换完成: {i+1}秒")
            sys.stdout.flush()
            
            response = requests.get(f"{SERVER_URL}/api/convert/status/{task_id}")
            
            if response.status_code != 200:
                print(f"\n❌ 获取状态失败: {response.status_code}")
                print(response.text)
                return None
            
            data = response.json()
            
            if data["status"] == "failed":
                print(f"\n❌ 转换失败: {data}")
                return None
            
            if data["status"] == "success":
                print(f"\n✅ 转换成功")
                return data
            
            time.sleep(1)
        
        print("\n❌ 转换超时")
        return None
    
    except Exception as e:
        print(f"\n❌ 检查状态异常: {e}")
        return None

def test_file_download(download_url):
    """测试文件下载功能"""
    print(f"\n正在测试文件下载: {download_url}")
    
    try:
        response = requests.get(f"{SERVER_URL}{download_url}")
        
        if response.status_code != 200:
            print(f"❌ 文件下载失败: {response.status_code}")
            print(response.text)
            return False
        
        content_length = len(response.content)
        print(f"✅ 文件下载成功，大小: {content_length} 字节")
        
        # 保存到临时文件以验证内容
        filename = download_url.split("/")[-1]
        temp_path = f"temp_{filename}"
        
        with open(temp_path, "wb") as f:
            f.write(response.content)
        
        print(f"✅ 文件已保存至: {temp_path}")
        return True
    
    except Exception as e:
        print(f"❌ 文件下载异常: {e}")
        return False

def test_file_preview(preview_url):
    """测试文件预览功能"""
    print(f"\n正在测试文件预览: {preview_url}")
    
    try:
        response = requests.get(f"{SERVER_URL}{preview_url}")
        
        if response.status_code != 200:
            print(f"❌ 文件预览失败: {response.status_code}")
            print(response.text)
            return False
        
        content_type = response.headers.get("Content-Type", "")
        content_length = len(response.content)
        
        print(f"✅ 文件预览成功，内容类型: {content_type}，大小: {content_length} 字节")
        return True
    
    except Exception as e:
        print(f"❌ 文件预览异常: {e}")
        return False

def run_test(name, file_path=None, url=None):
    """运行完整测试流程"""
    print(f"\n=== 开始测试: {name} ===")
    
    # 上传文件或下载URL
    if file_path:
        task_id = test_file_upload(file_path)
    elif url:
        task_id = test_url_download(url)
    else:
        print("❌ 未提供文件路径或URL")
        return False
    
    if not task_id:
        return False
    
    # 检查转换状态
    status_data = check_conversion_status(task_id)
    if not status_data:
        return False
    
    # 测试文件下载
    download_url = status_data.get("download_url")
    if download_url:
        if not test_file_download(download_url):
            return False
    else:
        print("❌ 未获取到下载URL")
        return False
    
    # 测试文件预览
    preview_url = status_data.get("preview_url")
    if preview_url:
        if not test_file_preview(preview_url):
            return False
    else:
        print("❌ 未获取到预览URL")
        return False
    
    print(f"\n=== 测试通过: {name} ===")
    return True

def main():
    """主测试函数"""
    if not check_server():
        print("\n请先启动服务器：python -m file_preview.cli.main server")
        return
    
    # 测试本地文件
    if os.path.exists(TEST_DOC):
        run_test("本地DOC文件", file_path=TEST_DOC)
    
    if os.path.exists(TEST_DOCX):
        run_test("本地DOCX文件", file_path=TEST_DOCX)
    
    if os.path.exists(TEST_XLS):
        run_test("本地XLS文件", file_path=TEST_XLS)
    
    if os.path.exists(TEST_XLSX):
        run_test("本地XLSX文件", file_path=TEST_XLSX)
    
    # 测试远程URL
    run_test("远程DOC文件", url=REMOTE_FILES["DOC"])
    run_test("远程DOCX文件", url=REMOTE_FILES["DOCX"])
    run_test("远程XLS文件", url=REMOTE_FILES["XLS"])
    run_test("远程XLSX文件", url=REMOTE_FILES["XLSX"])

if __name__ == "__main__":
    main() 