import os
import requests
import pandas as pd
import time

# 赛季 ID
SEASON_ID = "61627"
# 轮次范围
ROUNDS = range(1, 39)
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
        response = requests.get(url, timeout=10)  # 添加超时控制
        response.raise_for_status()  # 如果状态码不是 200，则抛出异常
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

def save_to_csv(data, round_number):
    """将比赛数据保存为 CSV"""
    file_path = os.path.join(SAVE_DIR, f"{round_number}.csv")

    # 如果 CSV 已存在且非空，跳过此轮
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        print(f"✅ Round {round_number} already exists, skipping.")
        return

    if not data:
        print(f"❌ No data found: Round {round_number}, creating an empty CSV.")
        pd.DataFrame().to_csv(file_path, index=False, encoding="utf-8")
        return

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding="utf-8")
    print(f"✅ Round {round_number} saved: {file_path}")

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
    for round_number in ROUNDS:
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
