from utils import convert_date_to_timestamp


cookie = "SINAGLOBAL=9379421760165.938.1718628607711; UOR=,,cn.bing.com; ULV=1724984016458:3:2:2:6368948829312.009.1724984016457:1724563951079; SCF=Aj4rbPQBJ4dcLANBbWQk4D8nBgzj2eCEGhNg3JxwWtzVTO3x6EaWt-VQjDKtLvbmRc7T146q461SK5MkW82JwxE.; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W58gYcZFnj-.ia.Az5L9aKu5JpX5KMhUgL.Fo-X1KqceKqXShB2dJLoIXBLxKqL1K.LB--LxK-L1h-LB-BLxKnL12eLBo.LxKBLB.eL122LxKqL1KqLB-qLxKMLBo2LBoeLxK-LBo5L1Kx9McfDMntt; ALF=1730974156; SUB=_2A25KAXScDeRhGeNK4lQX8SjIzziIHXVpf4hUrDV8PUJbkNANLXetkW1NSOnZECcz1xhidS1Arrgm2hR_W7908gKc; XSRF-TOKEN=5i1GIX2Zvz-BdlalfcRtWtmX; WBPSESS=OAW4AFAwG_TA9nc1bDQyfGxlC8uzmfQBiklrjU9r4GKmtZaBD-IuysLlaEbmwaUlI9Vpe8P2JypOZI1elKixEATk2qTMNhAmfHLmTgNVPrkBd3lvgE_B7HkkA2d2-AsITkfSnFkv_Pww_piQCpYB-Q=="

result_dir = './weibo_results'
start_date = convert_date_to_timestamp('2024-08-20')  # 开始时间，时间戳格式
end_date = convert_date_to_timestamp('2024-10-12')    # 结束时间，时间戳格式
download_images = True     # 是否下载图片
fetch_reposts = True       # 是否抓取转发微博

