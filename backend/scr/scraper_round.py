# check
import os
import requests
import pandas as pd
import time
import hashlib

# 赛季 ID
SEASON_ID = "61627"
# 目标文件夹
SAVE_DIR = f"backend/round/{SEASON_ID}"
os.makedirs(SAVE_DIR, exist_ok=True)

# API
API_URL_TEMPLATE = "https://www.sofascore.com/api/v1/unique-tournament/17/season/{}/events/round/{}"

# 失败轮次列表
failed_rounds = []

def fetch_data(round_number):
    """获取指定轮次的比赛数据"""
    url = API_URL_TEMPLATE.format(SEASON_ID, round_number)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Request failed: Round {round_number}, error: {e}")
        return None

def clean_data(data):
    """整理比赛数据，使其格式清晰可读"""
    if not data or "events" not in data:
        return []

    cleaned_data = []
    for event in data["events"]:
        match_info = {
            "Match ID": event.get("id"),
            "Round": event.get("roundInfo", {}).get("round", "N/A"),
            "Status": event.get("status", {}).get("description", "N/A"),
            "Start Timestamp": event.get("startTimestamp", "N/A"),
            "Home Team": event.get("homeTeam", {}).get("name", "N/A"),
            "Away Team": event.get("awayTeam", {}).get("name", "N/A"),
            "Home Score": event.get("homeScore", {}).get("current", "N/A"),
            "Away Score": event.get("awayScore", {}).get("current", "N/A"),
            "Final Result Only": event.get("finalResultOnly", "N/A"),
            "Has XG Data": event.get("hasXg", "N/A"),
            "Slug": event.get("slug", "N/A"),
        }
        cleaned_data.append(match_info)

    return cleaned_data

def calculate_hash(data):
    """计算数据的哈希值"""
    return hashlib.md5(pd.DataFrame(data).to_csv(index=False).encode()).hexdigest()

def get_existing_hash(file_path):
    """获取已存在的 CSV 文件的哈希值"""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return None
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def save_to_csv(data, round_number):
    """检查哈希值并决定是否更新 CSV 文件"""
    file_path = os.path.join(SAVE_DIR, f"{round_number}.csv")

    if not data:
        print(f"❌ No data found: Round {round_number}, creating an empty CSV.")
        pd.DataFrame().to_csv(file_path, index=False, encoding="utf-8")
        return

    new_hash = calculate_hash(data)
    old_hash = get_existing_hash(file_path)

    if old_hash == new_hash:
        print(f"✅ Round {round_number} data unchanged, skipping update.")
    else:
        pd.DataFrame(data).to_csv(file_path, index=False, encoding="utf-8")
        print(f"🔄 Round {round_number} updated: {file_path}")

def find_not_started_rounds():
    """扫描 CSV 文件，找出所有包含 Not Started 或 Postponed 状态的轮次"""
    not_started_rounds = set()
    
    for file_name in os.listdir(SAVE_DIR):
        if not file_name.endswith(".csv"):
            continue

        round_number = int(file_name.split(".")[0])
        file_path = os.path.join(SAVE_DIR, file_name)
        df = pd.read_csv(file_path)

        if "Status" in df.columns and "Round" in df.columns:
            if any(df["Status"].eq("Not Started")) or any(df["Status"].eq("Postponed")):
                not_started_rounds.add(round_number)

    return sorted(not_started_rounds)

def compute_update_rounds(not_started_rounds):
    """基于 Not Started 轮次计算需要更新的轮次（前后 2 轮）"""
    update_rounds = set()

    for round_number in not_started_rounds:
        for offset in range(-2, 3):  # 向前2轮，向后2轮
            new_round = round_number + offset
            if 1 <= new_round <= 38:  # 限制在 1-38 轮范围内
                update_rounds.add(new_round)

    return sorted(update_rounds)

def retry_failed_rounds():
    """重试失败的轮次"""
    global failed_rounds
    max_retries = 3  # 最大重试次数

    for attempt in range(1, max_retries + 1):
        if not failed_rounds:
            return  # 如果没有失败的轮次，提前返回

        print(f"\n🔄 Retrying {len(failed_rounds)} failed rounds (Attempt {attempt}/{max_retries})...\n")

        remaining_failures = []
        for round_number in failed_rounds:
            print(f"Retrying round {round_number}...")
            data = fetch_data(round_number)
            formatted_data = clean_data(data)
            
            if formatted_data or os.path.exists(os.path.join(SAVE_DIR, f"{round_number}.csv")):
                save_to_csv(formatted_data, round_number)
            else:
                print(f"❌ Round {round_number} still failed, will retry later.")
                remaining_failures.append(round_number)

        failed_rounds = remaining_failures  # 更新失败列表
        if failed_rounds:
            time.sleep(5)  # 休眠 5 秒再试下一轮
        else:
            print("✅ All failed rounds have been successfully fetched!")
            return

    if failed_rounds:
        print(f"⚠️ Some rounds still failed after retries: {failed_rounds}")

def main():
    print("🔍 Scanning for Not Started and Postponed rounds...")
    not_started_rounds = find_not_started_rounds()
    print(f"📝 Not Started/Postponed Rounds: {not_started_rounds}")

    update_rounds = compute_update_rounds(not_started_rounds)
    print(f"🔄 Rounds to update: {update_rounds}")

    for round_number in update_rounds:
        print(f"🔄 Fetching round {round_number} data...")
        data = fetch_data(round_number)
        formatted_data = clean_data(data)
        
        if not formatted_data:
            failed_rounds.append(round_number)  # 记录失败的轮次
        save_to_csv(formatted_data, round_number)

    # 运行完所有轮次后，重新尝试失败的轮次
    retry_failed_rounds()

if __name__ == "__main__":
    main()
