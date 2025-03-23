import requests
import pandas as pd

# 定义 API URL
url = "https://www.sofascore.com/api/v1/unique-tournament/17/season/61627/top-teams/overall"

# 发起请求并获取数据
response = requests.get(url)

# 检查响应状态
if response.status_code == 200:
    data = response.json()
    
    # 提取和整理数据
    top_teams_data = []
    for team_data in data['topTeams']['avgRating']:
        team_info = team_data['team']
        statistics = team_data['statistics']
        top_teams_data.append({
            "Team": team_info['name'],
            "Average Rating": statistics['avgRating'],
            "Matches Played": statistics['matches'],
            "Goals Scored": team_info.get('statistics', {}).get('goalsScored', 'N/A'),
            "Goals Conceded": team_info.get('statistics', {}).get('goalsConceded', 'N/A')
        })
    
    # 将数据转换为 pandas DataFrame
    df = pd.DataFrame(top_teams_data)
    
    # 设置文件保存路径
    output_path = "backend/data/61627/top_teams.csv"
    
    # 保存为 CSV 文件
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Data has been saved to {output_path}")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
