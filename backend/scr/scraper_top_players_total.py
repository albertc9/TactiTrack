import requests
import pandas as pd

# 定义 API URL
url = "https://www.sofascore.com/api/v1/unique-tournament/17/season/61627/top-players/overall"

# 发起请求并获取数据
response = requests.get(url)

# 检查响应状态
if response.status_code == 200:
    data = response.json()
    
    # 提取和整理数据
    top_players_data = []
    for player_data in data['topPlayers']['rating']:
        player_info = player_data['player']
        statistics = player_data['statistics']
        top_players_data.append({
            "Player": player_info['name'],
            "Team": player_data['team']['name'],
            "Position": player_info['position'],
            "Rating": statistics['rating'],
            "Appearances": statistics['appearances'],
            "User Count": player_info['userCount'],
        })
    
    # 将数据转换为 pandas DataFrame
    df = pd.DataFrame(top_players_data)
    
    # 设置文件保存路径
    output_path = "backend/data/61627/top_players.csv"
    
    # 保存为 CSV 文件
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Data has been saved to {output_path}")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
