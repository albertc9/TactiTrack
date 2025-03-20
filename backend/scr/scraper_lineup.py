import os
import csv
import requests
import time

# 设置基本路径
ROUND_DIR = "backend/round/61627"
LINEUP_DIR = "backend/data/lineup"
API_URL_TEMPLATE = "https://www.sofascore.com/api/v1/event/{match_id}/lineups"

# 失败比赛列表
failed_matches = []

def create_directory(path):
    """创建目录（如果不存在）"""
    if not os.path.exists(path):
        os.makedirs(path)

def fetch_lineup(match_id):
    """从API获取阵容数据"""
    url = API_URL_TEMPLATE.format(match_id=match_id)
    try:
        response = requests.get(url, timeout=10)  # 添加超时时间
        response.raise_for_status()  # 检查 HTTP 状态码
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 请求失败: {e}")
        return None

def process_match(round_number, match_id, status):
    """处理单场比赛的阵容数据"""
    round_path = os.path.join(LINEUP_DIR, str(round_number))
    create_directory(round_path)
    
    file_path = os.path.join(round_path, f"{match_id}.csv")

    # 如果文件已经存在，跳过
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        print(f"✅ Match {match_id} (Round {round_number}) lineup already exists, skipping.")
        return
    
    # 如果比赛尚未开始，创建空文件
    if status != "Ended":
        open(file_path, 'w').close()  # 创建空CSV文件
        print(f"Match {match_id} (Round {round_number}) not started, empty file created.")
        return
    
    lineup_data = fetch_lineup(match_id)
    if not lineup_data:
        print(f"❌ Failed to fetch lineup for match {match_id}. Adding to retry queue.")
        failed_matches.append((round_number, match_id, status))
        return
    
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Match ID", "Team", "Player Name", "Position", "Jersey Number", "Height", "Country", "Date of Birth", "Substitute", "Total Pass", "Accurate Pass", "Rating"])
        
        for team_key in ["home", "away"]:
            team_data = lineup_data.get(team_key, {})
            team_name = team_data.get("name", team_key.capitalize())
            players = team_data.get("players", [])
            
            for player_entry in players:
                player = player_entry.get("player", {})
                stats = player_entry.get("statistics", {})
                
                row = [
                    match_id,
                    team_name,
                    player.get("name", "Unknown"),
                    player.get("position", "Unknown"),
                    player.get("jerseyNumber", "Unknown"),
                    player.get("height", "Unknown"),
                    player.get("country", {}).get("name", "Unknown"),
                    player.get("dateOfBirthTimestamp", "Unknown"),
                    player_entry.get("substitute", False),
                    stats.get("totalPass", "Unknown"),
                    stats.get("accuratePass", "Unknown"),
                    stats.get("rating", "Unknown")
                ]
                writer.writerow(row)
    
    print(f"✅ Match {match_id} (Round {round_number}) lineup saved.")

def retry_failed_matches():
    """重试失败的比赛抓取"""
    global failed_matches
    max_retries = 3  # 最大重试次数

    for attempt in range(1, max_retries + 1):
        if not failed_matches:
            return  # 如果没有失败的比赛，提前返回

        print(f"\n🔄 重新尝试获取 {len(failed_matches)} 场失败的比赛 (第 {attempt}/{max_retries} 次)...\n")

        remaining_failures = []
        for round_number, match_id, status in failed_matches:
            print(f"Retrying match {match_id} (Round {round_number})...")
            lineup_data = fetch_lineup(match_id)
            
            if lineup_data:
                process_match(round_number, match_id, status)
            else:
                print(f"❌ Match {match_id} still failed, will retry later.")
                remaining_failures.append((round_number, match_id, status))

        failed_matches = remaining_failures  # 更新失败列表
        if failed_matches:
            time.sleep(5)  # 休眠 5 秒再试下一轮
        else:
            print("✅ 所有失败的比赛都成功获取！")
            return

    if failed_matches:
        print(f"⚠️ 仍然有 {len(failed_matches)} 场比赛失败，建议手动检查: {failed_matches}")

def main():
    """主函数：遍历所有轮次，获取比赛阵容数据"""
    for round_file in sorted(os.listdir(ROUND_DIR)):
        if not round_file.endswith(".csv"):
            continue
        
        round_number = round_file.split(".")[0]
        round_path = os.path.join(ROUND_DIR, round_file)
        
        with open(round_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                match_id = row["Match ID"].strip()
                status = row["Status"].strip()
                process_match(round_number, match_id, status)

    # 运行完所有比赛后，重新尝试失败的比赛
    retry_failed_matches()

if __name__ == "__main__":
    main()
