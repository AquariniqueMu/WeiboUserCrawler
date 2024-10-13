'''
Author: Junwen Yang
Date: 2024-10-13 22:33:56
LastEditors: Junwen Yang
LastEditTime: 2024-10-13 22:46:19
FilePath: \WeiboUserCrawl2\main_from_xlsx.py
Description: Collect User ID from Excel file and crawl Weibo data for each user.
'''


import os
import pandas as pd
import argparse
import time
import random
from weibo import WeiboCrawler
from config import cookie, result_dir, start_date, end_date, download_images, fetch_reposts


def run_weibo_crawler(excel_file, id_column):
    # 读取 Excel 文件并提取用户 ID 列
    df = pd.read_excel(excel_file)
    if id_column not in df.columns:
        print(f"列名 '{id_column}' 不存在于文件 '{excel_file}' 中，请检查列名。")
        return
    user_ids = df[id_column].astype(str).tolist()  # 确保用户 ID 为字符串类型

    print("=" * 50 + " Start Weibo Crawler " + "=" * 50 + "\n")

    for user_id in user_ids:
        print(f"开始抓取用户 {user_id} 的微博数据...")
        user_result_dir = os.path.join(result_dir, user_id)  # 为每个用户创建单独的结果目录

        config = {
            'user_id': user_id,
            'cookie': cookie,
            'result_dir': user_result_dir,
            'start_date': start_date,
            'end_date': end_date,
            'download_images': download_images,
            'fetch_reposts': fetch_reposts,
        }

        weibo_crawler = WeiboCrawler(config)
        weibo_crawler.start()

    print("\n" + "=" * 50 + " End Weibo Crawler " + "=" * 50)
    time.sleep(random.uniform(3,6))  # 随机等待3-6秒，避免被封号


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Weibo Crawler')

    # 在这里添加参数，指定你的 Excel 文件路径和用户 ID 列名
    parser.add_argument('--excel_file', type=str, default='user_ids.xlsx', help='Excel文件路径，默认值为 user_ids.xlsx')
    parser.add_argument('--id_column', type=str, default='用户ID', help='用户ID列名，默认值为 "用户ID"')

    args = parser.parse_args()

    run_weibo_crawler(args.excel_file, args.id_column)
