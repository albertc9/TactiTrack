import subprocess
import sys
import os

def run_script(script_path):
    """运行指定的 Python 脚本"""
    try:
        subprocess.run([sys.executable, script_path], check=True)
        print(f"✅ Run Successful! {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Run {script_path} Failed: {e}")

if __name__ == "__main__":
    script_dir = "backend/scr"  # 目标文件夹
    scripts = [
        os.path.join(script_dir, f) for f in os.listdir(script_dir)
        if f.endswith(".py") and f != "__init__.py"
    ]

    if not scripts:
        print("⚠️ No Python scripts found in backend/scr/")
    else:
        for script in sorted(scripts):  # 按文件名排序，确保顺序执行
            run_script(script)
    
    print("🎯 All scraper scripts have been executed！")
