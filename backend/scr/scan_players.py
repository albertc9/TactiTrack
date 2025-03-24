import os
import csv

# 设置路径
lineup_folder = "backend/data/lineup"
players_csv_path = "backend/data/61627/players.csv"

# 用于存储玩家的名字和ID
players = {}

# 扫描遍历 1-38 号文件夹中的所有 CSV 文件
for round_num in range(1, 39):
    round_folder_path = os.path.join(lineup_folder, str(round_num))

    # 如果文件夹存在，遍历该文件夹中的所有 CSV 文件
    if os.path.exists(round_folder_path):
        for filename in os.listdir(round_folder_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(round_folder_path, filename)

                # 打开并读取 CSV 文件
                with open(file_path, mode='r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    try:
                        # 先尝试跳过标题行
                        next(reader)  # 跳过标题行
                    except StopIteration:
                        # 如果文件为空，跳过当前文件
                        continue

                    # 遍历每一行，提取 Player Name 和 Player ID
                    for row in reader:
                        if len(row) >= 4:  # 确保文件不是空的，且至少有4列
                            player_name = row[3].strip()  # Player Name（第四列）
                            player_id = row[2].strip()    # Player ID（第三列）

                            # 添加到字典（如果 player_id 不存在）
                            if player_id not in players:
                                players[player_id] = player_name

# 创建 players.csv 文件，写入更新后的数据
with open(players_csv_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Player Name", "Player ID"])  # 写入标题行

    # 写入所有不重复的 Player Name 和 Player ID
    for player_id, player_name in players.items():
        writer.writerow([player_name, player_id])

print(f"Player data has been updated and saved to {players_csv_path}")
