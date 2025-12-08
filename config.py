# Z-Library 下载器配置文件
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# ============ 账号配置 ============
# 从环境变量读取敏感信息（存储在 .env 文件中）
EMAIL = os.getenv("ZLIB_EMAIL", "")
PASSWORD = os.getenv("ZLIB_PASSWORD", "")

# ============ 下载配置 ============
# 每日最大下载数量
DAILY_DOWNLOAD_LIMIT = 999

# 下载文件保存目录
DOWNLOAD_DIR = "./downloads"

# 每次请求之间的延迟（秒），设为0.5可加快速度
REQUEST_DELAY = 0.5

# 下载失败时的重试次数
MAX_RETRIES = 3

# 并发下载数量（同时下载几个文件，建议3-5个）
CONCURRENT_DOWNLOADS = 3

# ============ 搜索配置 ============
# 每页搜索结果数量
RESULTS_PER_PAGE = 50

# 搜索时默认最大页数
MAX_SEARCH_PAGES = 100

# 优先下载的文件格式（按优先级排序）
PREFERRED_FORMATS = ["epub", "pdf", "mobi", "azw3", "fb2", "djvu"]

# ============ 网络配置 ============
# Z-Library 主域名（如果访问不了可以尝试其他镜像）
BASE_URL = "https://z-library.la"

# 请求超时时间（秒）
TIMEOUT = 30

# 是否使用代理（如需要请配置）
USE_PROXY = False
PROXY = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}

# ============ 其他配置 ============
# Cookies 保存文件
COOKIES_FILE = "./cookies.json"

# 下载记录文件（避免重复下载）
DOWNLOAD_HISTORY_FILE = "./download_history.json"

# 是否跳过已下载的文件（True=跳过已下载，False=重新下载）
SKIP_DOWNLOADED = True

# 是否显示详细日志
VERBOSE = True

