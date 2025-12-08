# Python Web Scraping Learning Project

> ⚠️ **Disclaimer**: This project is for learning Python web scraping techniques only. Do not use it for illegally downloading copyrighted books. Please respect intellectual property rights and support official publications!

A sample project for learning Python web scraping techniques, covering core technologies such as HTTP requests, HTML parsing, concurrent programming, and session management.

## Language / 语言

[English](README.md) | [中文](README_CN.md)

## 📚 Learning Objectives

Through this project, you can learn the following core web scraping techniques:

- **HTTP Request Handling**: Using `requests` library for GET/POST requests
- **HTML Parsing**: Using `BeautifulSoup` to parse web content
- **Session Management**: Cookie persistence, login state maintenance
- **Concurrent Programming**: Multi-threaded downloads, thread pool management
- **Error Handling**: Network exception handling, automatic retry mechanism
- **Progress Display**: Beautiful terminal UI using `rich` library
- **Proxy Configuration**: HTTP/HTTPS proxy support

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| `requests` | HTTP request library |
| `BeautifulSoup` | HTML/XML parsing |
| `lxml` | High-performance parser |
| `rich` | Terminal beautification (progress bars, tables) |
| `ThreadPoolExecutor` | Concurrent downloads |
| `python-dotenv` | Environment variable management |

## Installation

```bash
# Navigate to project directory
cd ZLibrary-Spider

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### 1. Account Configuration (Required)

Copy `.env.example` to `.env` and edit it:

```bash
cp .env.example .env
```

Edit the `.env` file:

```bash
# Z-Library Account
ZLIB_EMAIL=your_email@example.com
ZLIB_PASSWORD=your_password
```

### 2. Download Settings (Optional)

Edit `config.py` to customize settings:

```python
# ============ Download Configuration ============
DAILY_DOWNLOAD_LIMIT = 300    # Daily download limit
DOWNLOAD_DIR = "./downloads"  # Download save directory
REQUEST_DELAY = 0.5           # Request interval (seconds)
MAX_RETRIES = 3               # Retry count on failure
CONCURRENT_DOWNLOADS = 3      # Concurrent download count (recommended 3-5)

# ============ Network Configuration ============
BASE_URL = "https://z-library.la"
TIMEOUT = 30
USE_PROXY = False
PROXY = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}
```

## Usage

### Start the Program

```bash
python zlib_downloader.py
```

### Available Commands (interactive)

| Command | Description | Example |
|---------|-------------|---------|
| `search <keyword> [start-end]` | Search multiple pages (default max pages from `config.MAX_SEARCH_PAGES`, currently 100) | `search Python`, `search Python 2-6`, `search Python 6` |
| `download <index/range/all>` | Download books | `download all` / `download 1-10` / `download 1,3,5` |
| `retry` | Retry failed downloads | `retry` |
| `login` | Manual login | `login` |
| `cookies <file_path>` | Import browser cookies | `cookies cookies.json` |
| `status` | View current status | `status` |
| `file <file_path>` | Batch search and download from file (one title per line) | `file books.txt` |
| `help` | Show help | `help` |
| `exit` | Exit program (or press Ctrl+C) | `exit` |

### Command Line Mode

```bash
# Search books (default up to config.MAX_SEARCH_PAGES pages)
python zlib_downloader.py -s "Python Programming"

# Search with custom max pages
python zlib_downloader.py -s "Python Programming" -p 20

# Search and download all results
python zlib_downloader.py -s "Python Programming" -d all

# Batch download from file
python zlib_downloader.py -f books.txt
```

### Download history & skipping
- `SKIP_DOWNLOADED` (config, default `True`): already-downloaded books are skipped.
- Skipped items are **not** counted as successful downloads; they appear separately in the statistics.

## 📖 Key Learning Points

### 1. HTTP Session Management

```python
self.session = requests.Session()
self.session.headers.update({
    "User-Agent": "Mozilla/5.0 ...",
    "Accept": "text/html,application/xhtml+xml...",
})
```

### 2. HTML Parsing

```python
soup = BeautifulSoup(resp.text, 'lxml')
book_cards = soup.find_all('z-bookcard')
```

### 3. Concurrent Downloads

```python
with ThreadPoolExecutor(max_workers=concurrent) as executor:
    futures = {executor.submit(download_worker, book): book for book in books}
    for future in as_completed(futures):
        result = future.result()
```

### 4. Error Retry Mechanism

```python
for attempt in range(max_retries):
    try:
        resp = self.session.get(url, timeout=config.TIMEOUT)
        # ...
    except requests.exceptions.ConnectionError:
        wait_time = config.REQUEST_DELAY * (2 ** attempt)  # Exponential backoff
        time.sleep(wait_time)
```

## File Structure

```
ZLibrary-Spider/
├── .env.example        # Environment variables template
├── config.py           # Configuration file
├── zlib_downloader.py  # Main program (core code)
├── requirements.txt    # Python dependencies
├── README.md           # Documentation (English)
├── README_CN.md        # Documentation (Chinese)
├── export_cookies.md   # Cookie export guide
└── downloads/          # Download directory
```

## FAQ

### Q: What to do if login fails?

1. Check if email and password are correct
2. **Manually import cookies** (recommended):
   - Install browser extension [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
   - Export cookies as JSON after logging in
   - Run: `cookies cookies.json`

### Q: Can't find any content?

1. Try using English keywords
2. Check network connection
3. Confirm target website is accessible

## ⚠️ Disclaimer

**This project is for learning Python web scraping techniques only!**

1. Do not use this project for illegally downloading copyrighted books
2. Please respect intellectual property rights and support official publications
3. Users are solely responsible for any legal consequences arising from the use of this project
4. This project does not provide any book resources, only demonstrates web scraping implementation

## 📜 License

MIT License - For educational purposes only
