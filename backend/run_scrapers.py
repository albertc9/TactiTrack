import subprocess
import sys

def run_script(script_name):
    """ 运行指定的 Python 脚本 """
    try:
        subprocess.run([sys.executable, script_name], check=True)
        print(f"✅ Run Successful! {script_name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Run {script_name} Failed: {e}")

if __name__ == "__main__":
    scripts = ["scraper_round.py", "scraper_lineup.py"]
    
    for script in scripts:
        run_script(script)
    
    print("🎯 All scraper scripts have been executed！")
