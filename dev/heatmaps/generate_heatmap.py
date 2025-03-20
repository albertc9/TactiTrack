import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
import seaborn as sns
import time

# Set base paths
DATA_PATH = "backend/data/match/player"
OUTPUT_PATH = "backend/heatmaps/61627"

# List to track failed tasks
failed_tasks = []

def draw_pitch(ax):
    """ Draw the football pitch """
    plt.plot([0, 0], [0, 90], color="black")
    plt.plot([0, 130], [90, 90], color="black")
    plt.plot([130, 130], [90, 0], color="black")
    plt.plot([130, 0], [0, 0], color="black")
    plt.plot([65, 65], [0, 90], color="black")

def generate_heatmap(csv_file, png_file, attempts=3):
    """ Generate the player heatmap """
    for attempt in range(attempts):
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(7, 5))
            draw_pitch(ax)
            
            if df.empty:
                print(f"{csv_file} is empty, generating a blank heatmap.")
            else:
                sns.kdeplot(x=df["x"] * 1.3, y=df["y"] * 0.9, fill=True, levels=50, cmap="Reds", alpha=1.0)
            
            # Set range and transparent background
            plt.xlim(0, 100)
            plt.ylim(0, 100)
            plt.axis('off')
            plt.savefig(png_file, dpi=150, bbox_inches="tight", transparent=True)
            plt.close()
            
            print(f"Successfully generated: {png_file}")
            return True  # Successfully generated, return True
        
        except Exception as e:
            print(f"Failed to generate {png_file} (Attempt {attempt + 1}/3): {e}")
            time.sleep(1)  # Wait 1 second before retrying
    
    # If all 3 attempts fail, record the failure
    failed_tasks.append((csv_file, png_file))
    return False

def process_heatmaps():
    """ Iterate through all player data and generate heatmaps """
    for round_id in os.listdir(DATA_PATH):
        round_path = os.path.join(DATA_PATH, round_id)
        
        if not os.path.isdir(round_path):
            continue
        
        for match_id in os.listdir(round_path):
            match_path = os.path.join(round_path, match_id)
            
            if not os.path.isdir(match_path):
                continue
            
            for player_id in os.listdir(match_path):
                if not player_id.endswith(".csv"):
                    continue
                
                player_csv = os.path.join(match_path, player_id)
                player_png = os.path.join(OUTPUT_PATH, round_id, match_id, player_id.replace(".csv", ".png"))
                
                # Ensure output directory exists
                os.makedirs(os.path.dirname(player_png), exist_ok=True)
                
                # Check if PNG already exists
                if os.path.exists(player_png):
                    print(f"{player_png} already exists, skipping.")
                    continue
                
                # Generate heatmap
                generate_heatmap(player_csv, player_png)

def retry_failed_tasks():
    """ Retry all failed tasks """
    global failed_tasks
    print("\nRetrying failed tasks...")
    
    remaining_failures = []
    for csv_file, png_file in failed_tasks:
        if not generate_heatmap(csv_file, png_file, attempts=1):
            remaining_failures.append((csv_file, png_file))
    
    failed_tasks = remaining_failures  # Update failed tasks list
    
    if failed_tasks:
        print("\nThe following files still failed to generate:")
        for csv_file, png_file in failed_tasks:
            print(f"CSV: {csv_file} -> PNG: {png_file}")
    else:
        print("All tasks completed successfully!")

if __name__ == "__main__":
    process_heatmaps()
    retry_failed_tasks()
