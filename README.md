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

## Quick Start

### Method 1: Using Browser Cookies (Recommended) ⭐

This is the simplest and most reliable method!

1. **Install browser extension**:
   - Chrome/Edge: Install [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
   - Firefox: Install [Cookie-Editor](https://addons.mozilla.org/firefox/addon/cookie-editor/)

2. **Login to Z-Library in browser** (https://z-library.la or https://z-library.ec)

3. **Export Cookies**:
   - Click extension icon
   - Click "Export"
   - Save as `browser_cookies.json`

4. **Run program and import cookies**:
   ```bash
   ./start.sh
   # In interactive mode, enter:
   cookies browser_cookies.json
   # Start searching and downloading
   search Python
   download all
   ```

### Method 2: Using Account Credentials (Optional)

If automatic login doesn't work, use Method 1 instead.

Edit `.env` file:
```bash
ZLIB_EMAIL=your_email@example.com
ZLIB_PASSWORD=your_password
```

## Configuration

Edit `config.py` to customize settings:

```python
# Download Configuration
DAILY_DOWNLOAD_LIMIT = 999    # Daily download limit
DOWNLOAD_DIR = "./downloads"  # Download save directory
REQUEST_DELAY = 0.5           # Request interval (seconds)
CONCURRENT_DOWNLOADS = 3      # Concurrent downloads

# Network Configuration
BASE_URL = "https://z-library.la"  # Primary domain
MIRROR_URLS = [                    # Backup domains
    "https://z-library.la",
    "https://z-library.ec"
]
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

### Q: Getting 503 error?

The website has enabled protection. Solutions:
1. **Import cookies** (recommended): Export cookies from browser after logging in
2. Wait a few hours and retry (protection is usually temporary)
3. If you have VPN, try using it

### Q: How to export browser cookies?

1. Install browser extension:
   - Chrome/Edge: [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
   - Firefox: Cookie-Editor
2. Login to Z-Library in browser
3. Click extension icon → Export → Save as JSON
4. In program, run: `cookies browser_cookies.json`

### Q: Program runs but search returns empty results?

1. Make sure you've imported valid cookies
2. Check if the website is accessible in your browser
3. Try exporting and importing cookies again

### Q: Slow download speed?

Adjust in `config.py`:
```python
CONCURRENT_DOWNLOADS = 5  # Increase concurrent downloads
REQUEST_DELAY = 0.3       # Reduce delay
```

## ⚠️ Disclaimer

**This project is for learning Python web scraping techniques only!**

1. Do not use this project for illegally downloading copyrighted books
2. Please respect intellectual property rights and support official publications
3. Users are solely responsible for any legal consequences arising from the use of this project
4. This project does not provide any book resources, only demonstrates web scraping implementation

## 📜 License

MIT License - For educational purposes only
