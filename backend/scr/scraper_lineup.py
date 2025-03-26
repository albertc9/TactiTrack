# check
import os
import csv
import requests
import time
import hashlib

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
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 请求失败: {e}")
        return None

def calculate_hash(file_path):
    """计算已有文件的哈希值"""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return None
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def compute_hash_for_data(data):
    """计算新数据的哈希值"""
    return hashlib.md5(str(data).encode()).hexdigest()

def find_not_started_rounds():
    """扫描 CSV 文件，找出所有包含 Not started 或 Postponed 状态的轮次"""
    not_started_rounds = set()
    
    for file_name in os.listdir(ROUND_DIR):
        if not file_name.endswith(".csv"):
            continue

        round_number = int(file_name.split(".")[0])
        file_path = os.path.join(ROUND_DIR, file_name)
        
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                status = row.get("Status", "").strip()
                if status == "Not started" or status == "Postponed":
                    not_started_rounds.add(round_number)
                    break  # 只要该轮次中有一场是 Not started/Postponed，就记录该轮

    return sorted(not_started_rounds)

def compute_update_rounds(not_started_rounds):
    """基于 Not started 轮次计算需要更新的轮次（前后 2 轮）"""
    update_rounds = set()

    for round_number in not_started_rounds:
        for offset in range(-2, 3):  # 向前2轮，向后2轮
            new_round = round_number + offset
            if 1 <= new_round <= 38:  # 限制在 1-38 轮范围内
                update_rounds.add(new_round)

    return sorted(update_rounds)

def process_match(round_number, match_id, status):
    """处理单场比赛的阵容数据"""
    round_path = os.path.join(LINEUP_DIR, str(round_number))
    create_directory(round_path)
    
    file_path = os.path.join(round_path, f"{match_id}.csv")

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
    
    # 计算新数据的哈希值
    new_hash = compute_hash_for_data(lineup_data)
    existing_hash = calculate_hash(file_path)

    if existing_hash == new_hash:
        print(f"✅ Match {match_id} (Round {round_number}) lineup unchanged, skipping.")
        return

    # 写入新的数据
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Match ID", "Team", "Player ID", "Player Name", "Position", "Jersey Number", "Height", "Country", "Date of Birth", "Substitute", "Total Pass", "Accurate Pass", "Rating", "AverageX", "AverageY"])
        
        for team_key in ["home", "away"]:
            team_data = lineup_data.get(team_key, {})
            team_name = team_data.get("name", team_key.capitalize())
            players = team_data.get("players", [])
            
            for player_entry in players:
                player = player_entry.get("player", {})
                stats = player_entry.get("statistics", {})

                # 提取正确的 averageX 和 averageY
                avg_x = player_entry.get("averageX", "Unknown")
                avg_y = player_entry.get("averageY", "Unknown")

                row = [
                    match_id,
                    team_name,
                    player.get("id", "Unknown"),  # 新增球员 ID
                    player.get("name", "Unknown"),
                    player.get("position", "Unknown"),
                    player.get("jerseyNumber", "Unknown"),
                    player.get("height", "Unknown"),
                    player.get("country", {}).get("name", "Unknown"),
                    player.get("dateOfBirthTimestamp", "Unknown"),
                    player_entry.get("substitute", False),
                    stats.get("totalPass", "Unknown"),
                    stats.get("accuratePass", "Unknown"),
                    stats.get("rating", "Unknown"),
                    avg_x,
                    avg_y
                ]
                writer.writerow(row)
    
    print(f"🔄 Match {match_id} (Round {round_number}) lineup updated.")

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
    print("🔍 Scanning for Not started and Postponed rounds...")
    not_started_rounds = find_not_started_rounds()
    print(f"📝 Not started/Postponed Rounds: {not_started_rounds}")

    update_rounds = compute_update_rounds(not_started_rounds)
    print(f"🔄 Rounds to update: {update_rounds}")

    for round_number in update_rounds:
        round_path = os.path.join(ROUND_DIR, f"{round_number}.csv")
        
        with open(round_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                match_id = row["Match ID"].strip()
                status = row["Status"].strip()
                process_match(round_number, match_id, status)

    # 运行完所有比赛后，重新尝试失败的比赛
    retry_failed_matches()

if __name__ == "__main__":
    main()
