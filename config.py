from utils import convert_date_to_timestamp


cookie = "your cookie"  # 微博cookie

result_dir = './weibo_results'
start_date = convert_date_to_timestamp('2024-08-20')  # 开始时间，时间戳格式
end_date = convert_date_to_timestamp('2024-10-12')    # 结束时间，时间戳格式
download_images = True     # 是否下载图片
fetch_reposts = True       # 是否抓取转发微博

