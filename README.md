# 微博用户爬虫项目

本项目是一个用于批量抓取微博用户微博数据的爬虫工具，支持从Excel文件中读取用户ID，抓取指定时间范围内的微博内容、图片等信息，并将结果保存到本地。现在，我们已经将项目封装为Docker容器，并开放了一个API接口，方便他人部署和使用。

## 目录

- [项目结构](#项目结构)
- [环境依赖](#环境依赖)
- [配置文件 `config.py`](#配置文件-configpy)
- [运行爬虫](#运行爬虫)
  - [1. 使用Docker部署和运行](#1-使用docker部署和运行)
    - [1.1 构建Docker镜像](#11-构建docker镜像)
    - [1.2 运行Docker容器](#12-运行docker容器)
    - [1.3 调用API接口](#13-调用api接口)
    - [1.4 查看结果](#14-查看结果)
  - [2. 直接运行Python脚本](#2-直接运行python脚本)
    - [2.1 抓取单个用户微博数据](#21-抓取单个用户微博数据)
    - [2.2 批量抓取多个用户微博数据](#22-批量抓取多个用户微博数据)
- [数据存储](#数据存储)
- [注意事项](#注意事项)
- [项目文件详解](#项目文件详解)
- [常见问题](#常见问题)
- [联系方式](#联系方式)
- [免责声明](#免责声明)
- [requirements.txt](#requirementstxt)

---

## 项目结构

```
WeiboUserCrawler/
├── app.py
├── config.py
├── Dockerfile
├── main_from_xlsx.py
├── main_single_user.py
├── requirements.txt
├── utils.py
├── weibo.py
└── weibo_results/ (empty, will be populated during runtime)
```

- `app.py`：Flask应用入口，提供API接口。
- `config.py`：配置文件，包含默认参数。
- `Dockerfile`：Docker镜像构建文件。
- `main_from_xlsx.py`：从Excel文件中读取用户ID，批量抓取微博数据的脚本。
- `main_single_user.py`：抓取单个用户微博数据的脚本。
- `requirements.txt`：Python依赖库列表。
- `utils.py`：工具函数，包含数据类型处理和日期转换等功能。
- `weibo.py`：微博爬虫核心代码，定义了`WeiboCrawler`类。
- `weibo_results/`：默认的数据保存目录，抓取的结果会存储在此文件夹中。

---

## 环境依赖

- Python 版本：**3.12.5**
- 依赖库：

  ```
  requests>=2.31.0
  pandas>=2.0.3
  tqdm>=4.65.0
  openpyxl>=3.1.2
  Flask>=2.0.3
  ```

  可使用以下命令安装依赖：

  ```bash
  pip install -r requirements.txt
  ```

---

## 配置文件 `config.py`

在使用爬虫前，需要配置`config.py`文件，包括Cookie、抓取时间范围等。

```python
from utils import convert_date_to_timestamp

# 默认的Cookie，可在运行时通过API传入
cookie = ""

result_dir = './weibo_results'
start_date = convert_date_to_timestamp('2023-01-01')  # 开始时间，格式：YYYY-MM-DD
end_date = convert_date_to_timestamp('2023-12-31')    # 结束时间，格式：YYYY-MM-DD
download_images = True     # 是否下载图片
fetch_reposts = True       # 是否抓取转发微博
```

---

## 运行爬虫

### 1. 使用Docker部署和运行

通过Docker容器化，您可以轻松地在任何支持Docker的环境中部署和运行本项目。

#### 1.1 构建Docker镜像

在项目根目录下，执行以下命令构建Docker镜像：

```bash
docker build -t weibo-crawler .
```

#### 1.2 运行Docker容器

使用以下命令运行Docker容器，并将结果目录映射到宿主机：

```bash
docker run -d -p 5000:5000 -v /your/host/path/weibo_results:/app/weibo_results --name weibo-crawler weibo-crawler
```

- `-d`：以守护进程方式运行容器。
- `-p 5000:5000`：将容器内的5000端口映射到宿主机的5000端口。
- `-v /your/host/path/weibo_results:/app/weibo_results`：将宿主机的目录映射到容器内的`/app/weibo_results`，用于数据持久化。
- `--name weibo-crawler`：为容器指定一个名称，方便管理。

**注意：**请将`/your/host/path/weibo_results`替换为您宿主机上用于存放结果的实际路径。

#### 1.3 调用API接口

使用`curl`命令或其他HTTP客户端（如Postman）发送POST请求：

```bash
curl -X POST http://localhost:5000/crawl \
     -H "Content-Type: application/json" \
     -d '{
           "user_id": "1234567890",
           "cookie": "YOUR_COOKIE_HERE",
           "start_date": "2023-01-01",
           "end_date": "2023-12-31",
           "download_images": true,
           "fetch_reposts": true
         }'
```

**参数说明：**

- `user_id`：必填，微博用户ID。
- `cookie`：必填，您的微博Cookie。
- `start_date`：选填，开始日期，格式`YYYY-MM-DD`。
- `end_date`：选填，结束日期，格式`YYYY-MM-DD`。
- `download_images`：选填，是否下载图片，默认为`false`。
- `fetch_reposts`：选填，是否抓取转发微博，默认为`false`。

**示例响应：**

```json
{
  "message": "Started crawling for user 1234567890"
}
```

#### 1.4 查看结果

抓取的结果会保存在宿主机的`/your/host/path/weibo_results`目录下，以用户ID命名的子目录中。

**查看容器日志：**

```bash
docker logs -f weibo-crawler
```

**停止容器：**

```bash
docker stop weibo-crawler
```

**启动容器：**

```bash
docker start weibo-crawler
```

**删除容器：**

```bash
docker rm weibo-crawler
```

---

### 2. 直接运行Python脚本

如果您希望在本地直接运行Python脚本，可以按照以下步骤操作。

#### 2.1 抓取单个用户微博数据

修改`main_single_user.py`中的`user_id`为目标用户的ID，然后运行该脚本。

```python
from weibo import WeiboCrawler
from config import cookie, result_dir, start_date, end_date, download_images, fetch_reposts

def run_weibo_crawler():
    user_id = '1234567890'  # 替换为目标用户的ID
    cookie = 'YOUR_COOKIE_HERE'  # 替换为你的Cookie

    config = {
        'user_id': user_id,
        'cookie': cookie,
        'result_dir': result_dir,
        'start_date': start_date,
        'end_date': end_date,
        'download_images': download_images,
        'fetch_reposts': fetch_reposts,
    }

    print("="*50 + " Start Weibo Crawler " + "="*50 + "\n")
    weibo_crawler = WeiboCrawler(config)
    weibo_crawler.start()
    print("\n" + "="*50 + " End Weibo Crawler " + "="*50)

if __name__ == "__main__":
    run_weibo_crawler()
```

**运行命令：**

```bash
python main_single_user.py
```

#### 2.2 批量抓取多个用户微博数据

将用户ID列表保存在Excel文件中，然后运行`main_from_xlsx.py`。

**准备Excel文件**

- 创建一个Excel文件（默认文件名：`user_ids.xlsx`）。
- 在第一列（默认列名：`用户ID`）中填写用户ID列表。

**运行脚本**

```bash
python main_from_xlsx.py --excel_file your_excel_file.xlsx --id_column 用户ID
```

- `--excel_file`：Excel文件路径，默认值为`user_ids.xlsx`。
- `--id_column`：用户ID列名，默认值为`用户ID`。

**示例：**

```bash
python main_from_xlsx.py
```

如果使用默认的文件名和列名，可以直接运行上述命令。

---

## 数据存储

- 所有抓取的结果会存储在`weibo_results/`目录下。
- 每个用户的数据会存放在以用户ID命名的子目录中。
- 数据包括：
  - 微博内容CSV文件：`weibo_用户ID.csv`
  - 图片文件：存储在对应微博ID的`images/`目录下。

---

## 注意事项

### 合法性与合规性

- **请遵守微博的服务条款和相关法律法规。**
- 本工具仅供学习和研究使用，禁止用于任何商业或非法用途。
- 请勿过度抓取，以免给微博服务器带来压力。

### 关于Cookie

- **安全性**：Cookie包含敏感信息，请妥善保管，避免泄露。
- **时效性**：Cookie可能会过期，若爬虫无法正常工作，请尝试更新Cookie。

### 请求频率

- 为避免触发微博的反爬机制，程序中已设置了随机等待时间。
- 如需调整，请在`weibo.py`的`start`方法中修改`time.sleep`的参数。

### 多线程与并发

- Docker部署的API接口中，每个爬虫任务在一个新线程中运行。
- 如果并发请求过多，可能会导致资源耗尽。
- 建议在`app.py`中增加任务队列或并发控制机制，限制同时运行的爬虫任务数量。

---

## 项目文件详解

### `app.py`

- Flask应用入口，提供了`/crawl` POST接口。
- 功能：
  - 接收请求参数：`user_id`、`cookie`、`start_date`、`end_date`等。
  - 启动一个新线程运行爬虫，避免阻塞API响应。
  - 返回JSON格式的响应，告知请求已开始处理。

### `weibo.py`

- 核心爬虫代码，定义了`WeiboCrawler`类。
- 功能：
  - 构造请求，获取微博数据。
  - 解析微博内容、用户信息、图片等。
  - 支持长微博处理，获取完整内容。
  - 可选择下载微博中的图片。

### `utils.py`

- 工具函数，包含：
  - `datatype_process`：数据类型转换，处理常见的数据格式。
  - `convert_date_to_timestamp`：将日期字符串转换为时间戳。

### `config.py`

- 配置文件，包含全局配置参数。
- 在Docker部署中，`cookie`和`user_id`等参数通过API接口传入。

### `main_single_user.py`

- 主程序，抓取单个用户的微博数据。
- 使用示例中，替换`user_id`和`cookie`为目标用户信息即可。

### `main_from_xlsx.py`

- 主程序，批量抓取多个用户的微博数据。
- 从指定的Excel文件中读取用户ID列表。

### `requirements.txt`

- Python依赖库列表，可使用`pip install -r requirements.txt`安装。

### `Dockerfile`

- Docker镜像构建文件。
- 指定了基础镜像、工作目录、依赖安装和启动命令。

### `weibo_results/`

- 数据保存目录。
- 程序运行后会自动创建，存储抓取的微博数据和图片。

---

## 常见问题

### 1. 爬虫无法抓取数据，提示Cookie错误

- 可能是Cookie过期，请重新获取并更新`config.py`中的`cookie`变量，或在API请求中传入最新的Cookie。

### 2. 运行程序时出现SSL错误

- 可能是网络问题或请求频率过高导致。
- 尝试降低请求频率，或在`weibo.py`中调整`verify=False`来忽略SSL验证（仅用于调试，不推荐长期使用）。

### 3. 如何获取用户ID

- 打开微博用户主页，浏览器地址栏中的一串数字即为用户ID。
- 也可以通过在线工具或API转换用户名为用户ID。

### 4. Docker容器无法启动或运行异常

- 请确保Docker已正确安装并正在运行。
- 检查`Dockerfile`和`docker run`命令的参数是否正确。
- 查看容器日志以获取更多错误信息：`docker logs -f weibo-crawler`

---

## 联系方式

如有问题或建议，欢迎联系项目作者。

- 作者：Junwen Yang
- 邮箱：lucas.junwen.yang@gmail.com

---

## 免责声明

- 本项目仅供学习和研究使用，禁止用于任何商业或非法用途。
- 使用本工具产生的任何风险和后果由用户自行承担，作者不承担任何责任。
