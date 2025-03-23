import requests
import pandas as pd
import json

# 定义 API URL
url = "https://www.sofascore.com/api/v1/team/7/team-statistics/seasons"

# 发起请求并获取数据
response = requests.get(url)

# 检查响应状态
if response.status_code == 200:
    data = response.json()

    # 提取所需数据
    seasons_data = []
    for tournament in data["uniqueTournamentSeasons"]:
        tournament_name = tournament["uniqueTournament"]["name"]
        for season in tournament["seasons"]:
            season_name = season["name"]
            year = season["year"]
            season_id = season["id"]
            seasons_data.append({
                "Tournament": tournament_name,
                "Season Name": season_name,
                "Year": year,
                "Season ID": season_id
            })

    # 将数据转换为 pandas DataFrame
    df = pd.DataFrame(seasons_data)

    # 保存为 CSV 文件
    output_path = "backend/data/season_pl.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Data has been saved to {output_path}")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
