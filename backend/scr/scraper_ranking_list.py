import requests
import pandas as pd

# 定义 API URL
url = "https://www.sofascore.com/api/v1/unique-tournament/17/season/61627/standings/total"

# 发起请求并获取数据
response = requests.get(url)

# 检查响应状态
if response.status_code == 200:
    data = response.json()
    
    # 提取所需数据
    standings_data = []
    for team in data['standings'][0]['rows']:
        team_info = team['team']
        standings_data.append({
            "Position": team["position"],
            "Team": team_info["name"],
            "Matches": team["matches"],
            "Wins": team["wins"],
            "Draws": team["draws"],
            "Losses": team["losses"],
            "Goals For": team["scoresFor"],
            "Goals Against": team["scoresAgainst"],
            "Goal Difference": team["scoreDiffFormatted"],
            "Points": team["points"],
            "Promotion": team["promotion"]["text"] if "promotion" in team else "None"
        })
    
    # 将数据转换为 pandas DataFrame
    df = pd.DataFrame(standings_data)
    
    # 设置文件保存路径
    output_path = "backend/data/season/61627.csv"
    
    # 保存为 CSV 文件
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Data has been saved to {output_path}")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
