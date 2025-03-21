import shutil
import os

src_root = 'backend/round/61647'
dst_root = 'frontend/static-data/round/61647'

os.makedirs(dst_root, exist_ok=True)

for filename in os.listdir(src_root):
    if filename.endswith('.csv'):
        shutil.copy(os.path.join(src_root, filename), os.path.join(dst_root, filename))
