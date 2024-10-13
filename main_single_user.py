'''
Author: Junwen Yang
Date: 2024-10-13 22:15:16
LastEditors: Junwen Yang
LastEditTime: 2024-10-13 22:48:55
FilePath: \WeiboUserCrawl2\main_single_user.py
Description: Run Weibo Crawler for a single user.
'''


from weibo import WeiboCrawler
from config import cookie, result_dir, start_date, end_date, download_images, fetch_reposts


def run_weibo_crawler():
    
    user_id = '5104872102'
    print(cookie)
    config = {
        'user_id': user_id,
        'cookie': cookie,
        'result_dir': result_dir,
        'start_date': start_date,
        'end_date': end_date,
        'download_images': download_images,
        'fetch_reposts': fetch_reposts,
    }
    print("="*50 + "Start Weibo Crawler" + "="*50 + "\n")

    weibo_crawler = WeiboCrawler(config)
    weibo_crawler.start()

    print("\n" + "="*50 + "End Weibo Crawler" + "="*50)


if __name__ == "__main__":
    run_weibo_crawler()