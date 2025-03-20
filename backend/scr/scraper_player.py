import os
import csv
import requests
import json
import pandas as pd
import time

# 基本路径
LINEUP_DIR = "backend/data/lineup"
PLAYER_DATA_DIR = "backend/data/match/player"
API_URL_TEMPLATE = "https://www.sofascore.com/api/v1/event/{match_id}/player/{player_id}/heatmap"

# 失败队列
failed_requests = []

def create_directory(path):
    """创建目录（如果不存在）"""
    if not os.path.exists(path):
        os.makedirs(path)

def fetch_heatmap(match_id, player_id):
    """从 API 获取球员热图数据"""
    url = API_URL_TEMPLATE.format(match_id=match_id, player_id=player_id)
    try:
        response = requests.get(url, timeout=10)  # 设置超时时间
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Failed to fetch heatmap: Match {match_id}, Player {player_id} - {e}")
        return None

def process_match(round_number, match_id, file_path):
    """处理单场比赛，提取球员 ID 并下载热图数据"""
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"❌ Error reading file {file_path}: {e}")
        return
    
    # 确保数据包含必要列
    required_columns = {"Player ID", "Substitute", "Rating"}
    if not required_columns.issubset(df.columns):
        print(f"⚠️ Skipping {file_path}: Required columns missing.")
        return

    # 遍历球员
    for _, row in df.iterrows():
        player_id = row["Player ID"]
        substitute = row["Substitute"]
        rating = row["Rating"]

        # 跳过无效的球员 ID
        if pd.isna(player_id) or str(player_id).strip() == "":
            continue

        # 目标存储路径
        save_path = os.path.join(PLAYER_DATA_DIR, str(round_number), str(match_id), f"{player_id}.csv")
        create_directory(os.path.dirname(save_path))

        # 如果球员是替补且没有评分，不请求 API，创建空 CSV
        if substitute == True and rating == "Unknown":
            open(save_path, 'w').close()  # 创建空 CSV
            print(f"ℹ️ Player {player_id} (Match {match_id}, Round {round_number}) was a substitute and did not play. Empty file created.")
            continue

        # 如果数据已存在，则跳过
        if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
            print(f"🔄 Heatmap already exists: {save_path}")
            continue

        # 获取热图数据
        heatmap_data = fetch_heatmap(match_id, player_id)
        if not heatmap_data or "heatmap" not in heatmap_data:
            print(f"❌ Failed to fetch heatmap for Match {match_id}, Player {player_id}. Adding to retry queue.")
            failed_requests.append((round_number, match_id, player_id))
            continue
        
        # 解析并存储
        heatmap_points = heatmap_data["heatmap"]
        if not heatmap_points:
            print(f"⚠️ Empty heatmap for Match {match_id}, Player {player_id}")
            continue
        
        # 转换为 DataFrame 并保存
        heatmap_df = pd.DataFrame(heatmap_points)
        heatmap_df.to_csv(save_path, index=False)
        print(f"✅ Heatmap saved: {save_path}")

def retry_failed_requests():
    """重试所有失败的热图抓取"""
    global failed_requests
    max_retries = 3  # 最大重试次数

    for attempt in range(1, max_retries + 1):
        if not failed_requests:
            return  # 如果没有失败的请求，提前返回

        print(f"\n🔄 Retrying {len(failed_requests)} failed heatmap requests (Attempt {attempt}/{max_retries})...\n")

        remaining_failures = []
        for round_number, match_id, player_id in failed_requests:
            print(f"Retrying: Match {match_id}, Player {player_id} (Round {round_number})...")
            heatmap_data = fetch_heatmap(match_id, player_id)

            if heatmap_data and "heatmap" in heatmap_data:
                save_path = os.path.join(PLAYER_DATA_DIR, str(round_number), str(match_id), f"{player_id}.csv")
                create_directory(os.path.dirname(save_path))
                heatmap_df = pd.DataFrame(heatmap_data["heatmap"])
                heatmap_df.to_csv(save_path, index=False)
                print(f"✅ Successfully retried and saved: {save_path}")
            else:
                print(f"❌ Match {match_id}, Player {player_id} still failed, will retry later.")
                remaining_failures.append((round_number, match_id, player_id))

        failed_requests = remaining_failures  # 更新失败列表
        if failed_requests:
            time.sleep(5)  # 休眠 5 秒后再试下一轮
        else:
            print("✅ All failed heatmap requests have been successfully retrieved!")
            return

    if failed_requests:
        print(f"⚠️ Still {len(failed_requests)} failed heatmap requests, manual check recommended: {failed_requests}")

def main():
    """主函数：遍历所有轮次，处理比赛数据"""
    for round_folder in range(1, 39):  # 遍历 1-38 轮
        round_path = os.path.join(LINEUP_DIR, str(round_folder))
        if not os.path.exists(round_path):
            print(f"⚠️ Skipping Round {round_folder}: Folder not found.")
            continue

        for match_file in os.listdir(round_path):
            if not match_file.endswith(".csv"):
                continue

            match_id = match_file.split(".")[0]
            file_path = os.path.join(round_path, match_file)
            process_match(round_folder, match_id, file_path)

    # 运行完所有比赛后，重新尝试失败的请求
    retry_failed_requests()

if __name__ == "__main__":
    main()
