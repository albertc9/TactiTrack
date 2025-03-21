import os
import shutil

# 定义需要复制的源路径和目标路径
copy_tasks = [
    {
        'src': 'backend/round/61647',
        'dst': 'frontend/static-data/round/61647'
    },
    {
        'src': 'backend/data/match',
        'dst': 'frontend/static-data/data/match'
    },
    {
        'src': 'backend/data/lineup',
        'dst': 'frontend/static-data/data/lineup'
    }
]

def copy_all(src_root, dst_root):
    if not os.path.exists(src_root):
        print(f"[跳过] 源路径不存在: {src_root}")
        return

    os.makedirs(dst_root, exist_ok=True)

    for root, dirs, files in os.walk(src_root):
        # 计算相对路径
        rel_path = os.path.relpath(root, src_root)
        dst_dir = os.path.join(dst_root, rel_path)

        os.makedirs(dst_dir, exist_ok=True)

        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dst_dir, file)
            shutil.copy2(src_file, dst_file)
            print(f"复制: {src_file} → {dst_file}")

print("🔁 正在复制静态数据用于 GitHub Pages 部署...\n")

for task in copy_tasks:
    copy_all(task['src'], task['dst'])

print("\n✅ 所有数据已复制完成！请确保 frontend/static-data/ 被提交至 GitHub。")
