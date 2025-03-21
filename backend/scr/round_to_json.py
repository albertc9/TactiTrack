import csv
import json
import os

# CSV 文件路径
csv_directory = 'backend/round/61627'

# 目标输出文件夹
output_directory = 'backend/round/61627/json'

def csv_to_json(csv_file, json_file):
    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        with open(json_file, mode='w', encoding='utf-8') as json_f:
            json.dump(rows, json_f, indent=4)

# 转换每一个 CSV 文件为 JSON
for round_num in range(1, 39):  # 处理 Round 1 到 Round 38
    csv_file = os.path.join(csv_directory, f'{round_num}.csv')
    json_file = os.path.join(output_directory, f'{round_num}.json')
    csv_to_json(csv_file, json_file)

print("CSV 转换为 JSON 完成！")
