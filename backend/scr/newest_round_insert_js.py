import csv
import os
import json

# 检查最新轮次并写入JS文件
def check_newest_round(csv_directory, js_file_path):
    # 从38.csv开始检查到1.csv
    for round_number in range(38, 0, -1):
        round_file = f"{round_number}.csv"
        round_file_path = os.path.join(csv_directory, round_file)

        # 确保文件存在
        if not os.path.exists(round_file_path):
            continue

        with open(round_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # 跳过表头

            # 检查每一行的Status列
            for row in reader:
                if row[2] == "Ended":  # 如果有一个"Ended"状态，则记录当前轮次
                    newest_round = round_number
                    print(f"最新的轮次是: Round {newest_round}")
                    write_newest_round_to_js(newest_round, js_file_path)
                    return  # 退出程序

    print("未找到已结束的轮次。")

# 将最新的轮次写入到JS文件
def write_newest_round_to_js(newest_round, js_file_path):
    with open(js_file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    # 查找 "const newestround_pl =" 这一行
    for i, line in enumerate(content):
        if "const newestround_pl =" in line:
            # 找到后，将数据插入到 newest_round_pl 变量中
            content[i] = f"const newestround_pl = [{newest_round}];\n"
            break

    # 将修改后的内容写回文件
    with open(js_file_path, 'w', encoding='utf-8') as file:
        file.writelines(content)

# 配置CSV文件目录和JS文件路径
csv_directory = "./backend/round/61627"  # 根据你的文件路径修改
js_file_path = "./frontend/js/scripts.js"  # 在前端项目中的路径

# 执行检查并写入JS
check_newest_round(csv_directory, js_file_path)
