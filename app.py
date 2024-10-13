'''
Author: Junwen Yang
Date: 2024-10-13 23:04:06
LastEditors: Junwen Yang
LastEditTime: 2024-10-13 23:04:12
FilePath: \WeiboUserCrawl\app.py
Description: 
'''
# app.py

from flask import Flask, request, jsonify
import os
import threading
from weibo import WeiboCrawler
from utils import convert_date_to_timestamp

app = Flask(__name__)

def run_crawler(config):
    crawler = WeiboCrawler(config)
    crawler.start()

@app.route('/crawl', methods=['POST'])
def crawl():
    data = request.json
    user_id = data.get('user_id')
    cookie = data.get('cookie')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    download_images = data.get('download_images', False)
    fetch_reposts = data.get('fetch_reposts', False)

    if not user_id or not cookie:
        return jsonify({'error': 'user_id and cookie are required'}), 400

    # 日期转换
    start_date = convert_date_to_timestamp(start_date_str) if start_date_str else None
    end_date = convert_date_to_timestamp(end_date_str) if end_date_str else None

    # 结果目录
    result_dir = os.path.join('./weibo_results', user_id)

    config = {
        'user_id': user_id,
        'cookie': cookie,
        'result_dir': result_dir,
        'start_date': start_date,
        'end_date': end_date,
        'download_images': download_images,
        'fetch_reposts': fetch_reposts,
    }

    # 启动爬虫线程
    threading.Thread(target=run_crawler, args=(config,)).start()

    return jsonify({'message': f'Started crawling for user {user_id}'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
