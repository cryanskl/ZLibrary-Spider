# Python 爬虫技术学习项目

> ⚠️ **声明**：本项目仅供学习 Python 爬虫技术使用，请勿用于非法下载版权书籍。请尊重知识产权，支持正版！

一个用于学习 Python 网络爬虫技术的示例项目，涵盖了 HTTP 请求、HTML 解析、并发编程、会话管理等核心技术。

## Language / 语言

[English](README.md) | [中文](README_CN.md)

## 📚 学习目标

通过本项目，你可以学习到以下爬虫核心技术：

- **HTTP 请求处理**：使用 `requests` 库发送 GET/POST 请求
- **HTML 解析**：使用 `BeautifulSoup` 解析网页内容
- **会话管理**：Cookie 持久化、登录状态维护
- **并发编程**：多线程下载、线程池管理
- **错误处理**：网络异常处理、自动重试机制
- **进度展示**：使用 `rich` 库实现美观的终端 UI
- **代理配置**：HTTP/HTTPS 代理支持

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| `requests` | HTTP 请求库 |
| `BeautifulSoup` | HTML/XML 解析 |
| `lxml` | 高性能解析器 |
| `rich` | 终端美化（进度条、表格） |
| `ThreadPoolExecutor` | 并发下载 |
| `python-dotenv` | 环境变量管理 |

## 安装

```bash
# 进入项目目录
cd ZLibrary-Spider

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

## 配置

### 1. 账号配置（必需）

复制 `.env.example` 为 `.env` 并编辑：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# Z-Library 账号
ZLIB_EMAIL=your_email@example.com
ZLIB_PASSWORD=your_password
```

### 2. 下载设置（可选）

编辑 `config.py` 文件自定义设置：

```python
# ============ 下载配置 ============
DAILY_DOWNLOAD_LIMIT = 300    # 每日下载上限
DOWNLOAD_DIR = "./downloads"  # 下载保存目录
REQUEST_DELAY = 0.5           # 请求间隔（秒）
MAX_RETRIES = 3               # 失败重试次数
CONCURRENT_DOWNLOADS = 3      # 并发下载数量（建议 3-5）

# ============ 网络配置 ============
BASE_URL = "https://z-library.la"
TIMEOUT = 30
USE_PROXY = False
PROXY = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}
```

## 使用方法

### 启动程序

```bash
python zlib_downloader.py
```

### 可用命令（交互模式）

| 命令 | 说明 | 示例 |
|------|------|------|
| `search <关键词> [起始页-结束页]` | 搜索多页（最大页数默认为 `config.MAX_SEARCH_PAGES`，当前 100） | `search Python` / `search Python 2-6` / `search Python 6` |
| `download <序号/范围/all>` | 下载书籍 | `download all` / `download 1-10` / `download 1,3,5` |
| `retry` | 重试失败的下载 | `retry` |
| `login` | 手动登录 | `login` |
| `cookies <文件路径>` | 导入浏览器 cookies | `cookies cookies.json` |
| `status` | 查看当前状态 | `status` |
| `file <文件路径>` | 从文件批量搜索下载（文件内一行一个书名） | `file books.txt` |
| `help` | 查看帮助 | `help` |
| `exit` | 退出程序（或按 Ctrl+C） | `exit` |

### 命令行模式

```bash
# 搜索书籍（默认最多搜索 config.MAX_SEARCH_PAGES 页）
python zlib_downloader.py -s "Python编程"

# 指定最大页数
python zlib_downloader.py -s "Python编程" -p 20

# 搜索并下载所有结果
python zlib_downloader.py -s "Python编程" -d all

# 从文件批量下载
python zlib_downloader.py -f books.txt
```

### 下载历史与跳过
- `SKIP_DOWNLOADED`（config，默认 `True`）：已下载过的书会被跳过。
- 跳过的条目不会计入成功下载数，统计中会单独显示跳过数量。

## 📖 代码学习要点

### 1. HTTP 会话管理

```python
self.session = requests.Session()
self.session.headers.update({
    "User-Agent": "Mozilla/5.0 ...",
    "Accept": "text/html,application/xhtml+xml...",
})
```

### 2. HTML 解析

```python
soup = BeautifulSoup(resp.text, 'lxml')
book_cards = soup.find_all('z-bookcard')
```

### 3. 并发下载

```python
with ThreadPoolExecutor(max_workers=concurrent) as executor:
    futures = {executor.submit(download_worker, book): book for book in books}
    for future in as_completed(futures):
        result = future.result()
```

### 4. 错误重试机制

```python
for attempt in range(max_retries):
    try:
        resp = self.session.get(url, timeout=config.TIMEOUT)
        # ...
    except requests.exceptions.ConnectionError:
        wait_time = config.REQUEST_DELAY * (2 ** attempt)  # 指数退避
        time.sleep(wait_time)
```

## 文件说明

```
ZLibrary-Spider/
├── .env.example        # 环境变量模板
├── config.py           # 配置文件
├── zlib_downloader.py  # 主程序（核心代码）
├── requirements.txt    # Python 依赖
├── README.md           # 说明文档（英文）
├── README_CN.md        # 说明文档（中文）
├── export_cookies.md   # Cookies 导出指南
└── downloads/          # 下载目录
```

## 常见问题

### Q: 登录失败怎么办？

1. 检查邮箱密码是否正确
2. **手动导入 cookies**（推荐）：
   - 安装浏览器扩展 [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
   - 登录后导出 cookies 为 JSON
   - 运行：`cookies cookies.json`

### Q: 搜索不到内容？

1. 尝试使用英文关键词
2. 检查网络连接
3. 确认目标网站可访问

## ⚠️ 免责声明

**本项目仅供学习 Python 爬虫技术使用！**

1. 请勿将本项目用于非法下载版权书籍
2. 请尊重知识产权，支持正版图书
3. 使用本项目产生的任何法律责任由使用者自行承担
4. 本项目不提供任何书籍资源，仅演示爬虫技术实现

## 📜 License

MIT License - 仅供学习交流使用
