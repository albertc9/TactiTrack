import csv
import os
import json
from datetime import datetime

# 读取CSV文件并将数据转换为合适的JSON格式
def parse_csv_to_json(csv_directory):
    rounds = []
    
    for round_file in os.listdir(csv_directory):
        if round_file.endswith(".csv"):
            round_number = int(round_file.split('.')[0])  # 转换为整数以便排序
            round_file_path = os.path.join(csv_directory, round_file)
            
            with open(round_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                matches = []
                for row in reader:
                    match = {
                        'match_id': row['Match ID'],
                        'round': row['Round'],
                        'status': row['Status'],
                        'start_timestamp': int(row['Start Timestamp']),
                        'home_team': row['Home Team'],
                        'away_team': row['Away Team'],
                        'home_score': row['Home Score'],
                        'away_score': row['Away Score'],
                    }
                    matches.append(match)
                rounds.append({'round_number': round_number, 'matches': matches})
    
    # 排序轮次（按round_number排序）
    rounds.sort(key=lambda x: x['round_number'])

    return rounds

# 将数据写入scripts.js
def write_to_js(data, js_file_path):
    with open(js_file_path, 'r', encoding='utf-8') as file:
        # 读取现有的JS文件内容
        content = file.readlines()

    # 查找 "const matchData =" 这一行
    for i, line in enumerate(content):
        if "const matchData =" in line:
            # 找到后，将数据插入到 matchData 变量中
            # 使用 json.dumps(data) 转换成单行 JSON 格式
            content[i] = "const matchData = " + json.dumps(data, separators=(',', ':')) + ";\n"
            break

    # 将修改后的内容写回文件
    with open(js_file_path, 'w', encoding='utf-8') as file:
        file.writelines(content)

# 解析CSV并写入文件
csv_directory = "./backend/round/61627"  # 根据你的文件路径修改
rounds_data = parse_csv_to_json(csv_directory)
js_file_path = "./frontend/js/scripts.js"  # 在前端项目中的路径
write_to_js(rounds_data, js_file_path)

print(f"数据已成功写入 {js_file_path}")
