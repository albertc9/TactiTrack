# check
import os
import csv
import requests
import pandas as pd

# 定义获取统计数据的 API URL 模板
url_template = "https://www.sofascore.com/api/v1/event/{}/statistics"

# 设置 CSV 文件路径
rounds_path = "backend/round/61627"
statistics_path = "backend/data/match/statistics"

# 遍历每个轮次的文件
for round_num in range(1, 39):
    round_filename = f"{round_num}.csv"
    round_file_path = os.path.join(rounds_path, round_filename)

    # 读取每个文件中的 Match ID
    with open(round_file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过标题行
        match_ids = [row[0] for row in reader]

    # 创建轮次文件夹
    round_folder = os.path.join(statistics_path, str(round_num))
    os.makedirs(round_folder, exist_ok=True)

    # 对每个 Match ID 获取统计数据
    for match_id in match_ids:
        api_url = url_template.format(match_id)
        response = requests.get(api_url)
        
        if response.status_code == 200:
            stats_data = response.json()
            statistics_items = []

            # 提取统计数据
            for period in stats_data['statistics']:
                for group in period['groups']:
                    for item in group['statisticsItems']:
                        statistics_items.append({
                            'name': item['name'],
                            'home': item['home'],
                            'away': item['away'],
                            'period': period['period'],
                            'groupName': group['groupName'],
                        })

            # 将统计数据保存为 CSV 文件
            stats_df = pd.DataFrame(statistics_items)
            match_file_path = os.path.join(round_folder, f"{match_id}.csv")
            stats_df.to_csv(match_file_path, index=False, encoding="utf-8")
            print(f"Saved statistics for Match ID {match_id} to {match_file_path}")
        else:
            print(f"Failed to fetch data for Match ID {match_id}")
