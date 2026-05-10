"""
自动更新 requirements.txt 脚本
运行此脚本会将当前环境的依赖同步到项目根目录的 requirements.txt
"""
import subprocess
import os
import sys

def update_requirements():
    print("🔄 正在扫描当前环境依赖...")
    try:
        # 获取当前环境的依赖列表
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        # 确定项目根目录（假设 scripts 在根目录下）
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        req_path = os.path.join(root_dir, "requirements.txt")
        
        # 写入文件
        with open(req_path, "w", encoding="utf-8") as f:
            f.write(result.stdout)
            
        print(f"✅ 成功更新: {req_path}")
        print(f"📦 共包含 {len(result.stdout.splitlines())} 个依赖包")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 更新失败: {e}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    update_requirements()
