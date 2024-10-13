import requests
import os
import csv
import logging
import random
import time
from datetime import datetime
from utils import datatype_process, convert_date_to_timestamp
from tqdm import tqdm  # 需要安装 tqdm 库
import warnings

warnings.filterwarnings("ignore")

# 配置日志
formatter = logging.Formatter(
    fmt='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class WeiboCrawler:
    def __init__(self, config):
        self.config = config
        self.user_id = config.get('user_id')
        self.cookie = config.get('cookie')
        self.result_dir = config.get('result_dir', './weibo_results')
        self.start_date = config.get('start_date')
        self.end_date = config.get('end_date')
        self.download_images = config.get('download_images', False)
        self.fetch_reposts = config.get('fetch_reposts', False)
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "close",
            "Cookie": self.cookie,
            "Pragma": "no-cache",
            "Referer": f"https://weibo.com/u/{self.user_id}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "X-Requested-With": "XMLHttpRequest",
        }
        # 创建结果目录
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)
        self.csv_file = os.path.join(self.result_dir, f'weibo_{self.user_id}.csv')
        self.base_url = "https://weibo.com/ajax/statuses/searchProfile"
        self.session = requests.Session()

        # 检查重要配置项
        assert self.user_id is not None, "用户ID（user_id）不能为空"
        assert self.cookie is not None, "Cookie 不能为空"
        assert isinstance(self.start_date, int), "开始日期（start_date）应为时间戳格式的整数"
        assert isinstance(self.end_date, int), "结束日期（end_date）应为时间戳格式的整数"

    def get_params(self, page):
        params = {
            "uid": self.user_id,
            "page": page,
            "starttime": self.start_date,
            "endtime": self.end_date,
            "hasori": 1,
            "hasret": 1 if self.fetch_reposts else 0,
            "hastext": 1,
            "haspic": 1,
            "hasvideo": 1,
            "hasmusic": 1
        }
        return params

    def fetch_data(self, page):
        params = self.get_params(page)
        try:
            response = self.session.get(self.base_url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            json_data = response.json()
            if 'data' in json_data and 'list' in json_data['data']:
                return json_data['data']['list']
            else:
                logger.warning("未获取到数据列表")
                return []
        except requests.RequestException as e:
            logger.error(f"请求错误：{e}")
            return []

    def get_long_weibo(self, id):
        """Fetch long Weibo."""
        for i in range(5):
            url = f"https://weibo.com/ajax/statuses/longtext?id={id}"
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                json_data = response.json()
                if 'data' in json_data:
                    return json_data['data']
                else:
                    logger.warning("未获取到长微博数据")
                    return None
            except requests.RequestException as e:
                logger.error(f"请求错误：{e}")
                return None

    def extract_weibo_content(self, weibo_json):
        weibo_text = weibo_json.get('text_raw')
        topics = []
        urls = []
        if_long_text = datatype_process(weibo_json.get('isLongText'), "bool")
        html_text = weibo_json.get('text')
        
        if if_long_text and "展开" in html_text:
            long_weibo_data = self.get_long_weibo(weibo_json.get('id'))
            if long_weibo_data:
                weibo_text = long_weibo_data.get('longTextContent', weibo_text)
                # Now extract topics and urls from long_weibo_data
                if long_weibo_data.get('topic_struct') and len(long_weibo_data.get('topic_struct')) > 0:
                    topics = [t.get('topic_title') for t in long_weibo_data.get('topic_struct', [])]
                if long_weibo_data.get('url_struct') and len(long_weibo_data.get('url_struct')) > 0:
                    urls = [(u.get('url_title'), u.get('ori_url')) for u in long_weibo_data.get('url_struct', [])]
            else:
                logger.warning("获取长微博数据失败，使用原始微博数据")
                if weibo_json.get('topic_struct'):
                    topics = [t.get('topic_title') for t in weibo_json.get('topic_struct', [])]
                if weibo_json.get('url_struct'):
                    urls = [(u.get('url_title'), u.get('ori_url')) for u in weibo_json.get('url_struct', [])]
        else:
            # Extract topics and urls from the weibo_json (non-long weibo)
            if weibo_json.get('topic_struct'):
                topics = [t.get('topic_title') for t in weibo_json.get('topic_struct', [])]
            if weibo_json.get('url_struct'):
                urls = [(u.get('url_title'), u.get('ori_url')) for u in weibo_json.get('url_struct', [])]

        return weibo_text, topics, urls

    def parse_single_weibo(self, weibo_json):
        data = {}
        data['weiboid'] = weibo_json.get('id')
        data['time'] = weibo_json.get("created_at")
        data['weibo_source'] = weibo_json.get("source")
        data['weibo_reposts_cnt'] = datatype_process(weibo_json.get("reposts_count"), "int")
        data['weibo_comments_cnt'] = datatype_process(weibo_json.get("comments_count"), "int")
        data['weibo_attitudes_cnt'] = datatype_process(weibo_json.get("attitudes_count"), "int")
        data['weibo_is_long_text'] = datatype_process(weibo_json.get("isLongText"), "bool")
        data['weibo_region_name'] = weibo_json.get("region_name")

        # Process user info
        userinfo = weibo_json.get("user", {})
        data['userinfo_id'] = userinfo.get("id")
        data['userinfo_name'] = userinfo.get("screen_name")
        data['userinfo_total_cnt_format'] = userinfo.get("status_total_counter", {}).get("total_cnt_format")
        data['userinfo_comment_cnt'] = datatype_process(userinfo.get("status_total_counter", {}).get("comment_cnt"), "int")
        data['userinfo_like_cnt'] = datatype_process(userinfo.get("status_total_counter", {}).get("like_cnt"), "int")
        data['userinfo_repost_cnt'] = datatype_process(userinfo.get("status_total_counter", {}).get("repost_cnt"), "int")
        data['userinfo_mbrank'] = datatype_process(userinfo.get("mbrank"), "int")
        data['userinfo_mbtype'] = datatype_process(userinfo.get("mbtype"), "int")

        # Get text, topics, urls
        weibo_text, topics, urls = self.extract_weibo_content(weibo_json)

        data['weibo_text'] = weibo_text
        data['topics'] = topics
        data['urls'] = urls

        return data

    def parse_weibo(self, weibo_json):
        try:
            # Parse main weibo
            main_weibo_data = self.parse_single_weibo(weibo_json)
            data = main_weibo_data

            # Process retweeted weibo
            if weibo_json.get("retweeted_status"):
                retweeted_weibo_json = weibo_json.get("retweeted_status")
                retweeted_data = self.parse_single_weibo(retweeted_weibo_json)
                # Prefix keys with 'retweeted_weibo_'
                retweeted_data_prefixed = {'retweeted_weibo_' + k: v for k, v in retweeted_data.items()}
                data.update(retweeted_data_prefixed)
            else:
                # No retweeted weibo, fill in empty values
                retweeted_keys = ['weiboid', 'time', 'weibo_source', 'weibo_reposts_cnt', 'weibo_comments_cnt', 'weibo_attitudes_cnt', 'weibo_is_long_text', 'weibo_region_name', 'weibo_text', 'topics', 'urls', 'userinfo_id', 'userinfo_name', 'userinfo_total_cnt_format', 'userinfo_comment_cnt', 'userinfo_like_cnt', 'userinfo_repost_cnt', 'userinfo_mbrank', 'userinfo_mbtype']
                for key in retweeted_keys:
                    data['retweeted_' + key] = ''

            # Handle image download
            if self.download_images and weibo_json.get("pic_infos"):
                self.download_images_func(weibo_json.get("pic_infos"), data['userinfo_id'], data['weiboid'], data['userinfo_name'])

            return data
        except AssertionError as ae:
            logger.error(f"数据检查失败：{ae}")
            return None
        except Exception as e:
            logger.error(f"解析微博数据时出错：{e}")
            return None

    def download_images_func(self, pic_infos, user_id, weibo_id, user_name):
        images_dir = os.path.join(self.result_dir, str(user_id), str(weibo_id), "images")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        for pic_id, pic_value in pic_infos.items():
            pic_url = pic_value.get("large", {}).get("url")
            if pic_url:
                try:
                    pic_response = self.session.get(pic_url, headers=self.headers, timeout=10)
                    pic_response.raise_for_status()
                    with open(os.path.join(images_dir, pic_id + ".jpg"), "wb") as f:
                        f.write(pic_response.content)
                    logger.info(f"成功抓取微博用户 {user_name} / 微博 {weibo_id} / 图片 {pic_id}")
                except requests.RequestException as e:
                    logger.error(f"下载图片失败：{e}")
            else:
                logger.warning("未找到图片URL")

    def write_csv_header(self, data):
        with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(data.keys())

    def write_csv_row(self, data):
        with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(data.values())

    def start(self):
        page = 1
        max_empty_pages = 5  # 最大允许连续空页面数量
        empty_page_count = 0
        total_weibo = 0
        pbar = tqdm(desc="抓取进度", unit="页", ncols=100, colour='green')

        while True:
            logger.info(f"正在抓取第 {page} 页微博...")
            weibo_list = self.fetch_data(page)
            if weibo_list:
                if page == 1 and not os.path.exists(self.csv_file):
                    # 写入CSV表头
                    first_weibo = self.parse_weibo(weibo_list[0])
                    if first_weibo:
                        self.write_csv_header(first_weibo)
                for weibo_json in weibo_list:
                    weibo_data = self.parse_weibo(weibo_json)
                    if weibo_data:
                        self.write_csv_row(weibo_data)
                        total_weibo += 1
                        logger.info(f"成功抓取微博用户 {weibo_data['userinfo_name']} / 微博 {weibo_data['weiboid']}")
                empty_page_count = 0
                page += 1
                pbar.update(1)
                time.sleep(random.uniform(0.5, 1.5))
            else:
                empty_page_count += 1
                if empty_page_count >= max_empty_pages:
                    logger.info("连续多页无数据，结束抓取。")
                    break
                else:
                    logger.info("本页无数据，继续下一页。")
                    page += 1
                    pbar.update(1)
                    time.sleep(1)
        pbar.close()
        logger.info(f"微博抓取完成，共抓取 {total_weibo} 条微博。")

if __name__ == "__main__":
    # 配置参数
    config = {
        'user_id': '5104872102',  # 替换为目标用户的ID
        'cookie': 'SINAGLOBAL=9379421760165.938.1718628607711; UOR=,,cn.bing.com; ULV=1724984016458:3:2:2:6368948829312.009.1724984016457:1724563951079; SCF=Aj4rbPQBJ4dcLANBbWQk4D8nBgzj2eCEGhNg3JxwWtzVTO3x6EaWt-VQjDKtLvbmRc7T146q461SK5MkW82JwxE.; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W58gYcZFnj-.ia.Az5L9aKu5JpX5KMhUgL.Fo-X1KqceKqXShB2dJLoIXBLxKqL1K.LB--LxK-L1h-LB-BLxKnL12eLBo.LxKBLB.eL122LxKqL1KqLB-qLxKMLBo2LBoeLxK-LBo5L1Kx9McfDMntt; ALF=1730974156; SUB=_2A25KAXScDeRhGeNK4lQX8SjIzziIHXVpf4hUrDV8PUJbkNANLXetkW1NSOnZECcz1xhidS1Arrgm2hR_W7908gKc; XSRF-TOKEN=5i1GIX2Zvz-BdlalfcRtWtmX; WBPSESS=OAW4AFAwG_TA9nc1bDQyfGxlC8uzmfQBiklrjU9r4GKmtZaBD-IuysLlaEbmwaUlI9Vpe8P2JypOZI1elKixEC9eVRRIU81n1qNJEBsecqNzbPtL5eddVEpXpe4atiDHplXfZCRwVw2pWQIwDw7MmA==',  # 替换为你的Cookie
        'result_dir': './weibo_results',
        'start_date': convert_date_to_timestamp('2024-08-20'),  # 开始时间，时间戳格式
        'end_date': convert_date_to_timestamp('2024-10-12'),    # 结束时间，时间戳格式
        'download_images': True,     # 是否下载图片
        'fetch_reposts': True,       # 是否抓取转发微博
    }
    crawler = WeiboCrawler(config)
    crawler.start()
