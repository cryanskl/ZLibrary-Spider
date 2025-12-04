# Z-Library Batch Downloader

A powerful batch download tool for Z-Library e-books, supporting concurrent downloads, multi-page search, resume capability, and more.

## Language / 语言

[English](README.md) | [中文](README_CN.md)

## Features

- ✅ **Account Login**: Automatic login with saved session state
- ✅ **Keyword Search**: Support single-page and multi-page batch search
- ✅ **Batch Download**: Support single, multiple, range selection, and download all
- ✅ **Concurrent Downloads**: Multi-threaded simultaneous downloads for significantly improved speed
- ✅ **Progress Display**: Real-time download progress and speed
- ✅ **Auto Retry**: Automatic retry on network errors, manual retry for failed items
- ✅ **Resume Capability**: Automatically skip already downloaded files
- ✅ **Daily Limit Tracking**: Automatically record download count
- ✅ **Filename Optimization**: Automatically remove `(Z-Library)` suffix
- ✅ **Proxy Support**: Support HTTP/HTTPS proxy

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

Edit the `config.py` file:

```python
# ============ Account Configuration ============
EMAIL = "your_email@example.com"
PASSWORD = "your_password"

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

### Configuration Guide

| Configuration | Description | Recommended Value |
|---------------|-------------|-------------------|
| `DAILY_DOWNLOAD_LIMIT` | Daily download limit | Set according to account level |
| `REQUEST_DELAY` | Request interval (seconds) | 0.3-1.0 |
| `CONCURRENT_DOWNLOADS` | Concurrent download count | 3-5 |
| `MAX_RETRIES` | Retry count on failure | 3-5 |

## Usage

### Start the Program

```bash
python zlib_downloader.py
```

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `search <keyword>` | Search books (page 1 only) | `search Python` |
| `searchall <keyword> [pages]` | Search multiple pages | `searchall Python 6` |
| `searchall <keyword> [start-end]` | Search specified page range | `searchall Python 2-6` |
| `download <index/range/all>` | Download books | `download all` / `download 1-10` / `download 1,3,5` |
| `retry` | Retry failed downloads | `retry` |
| `login` | Manual login | `login` |
| `cookies <file_path>` | Import browser cookies | `cookies cookies.json` |
| `status` | View current status | `status` |
| `file <file_path>` | Batch search and download from file | `file books.txt` |
| `help` | Show help | `help` |
| `exit` | Exit program | `exit` |

### Usage Examples

#### Example 1: Search and Download All Results

```
Z-Lib> search machine learning
Searching: machine learning (Page 1)...
Found 50 books

Z-Lib> download all
Starting batch download of 50 books...
Concurrent downloads: 3

Total Progress (15/50) ━━━━━━━━━━━━━━━━ 30%
#1 Machine Learning in Action... ━━━━━━━━━━━━━━ 45% 12.5 MB/s
#2 Deep Learning... ━━━━━━━━━━━━━━━━━━ 23% 8.2 MB/s
#3 Statistical Learning Methods... ━━━━━━━━━━━━━ 67% 15.1 MB/s

Download complete!
  Success: 48
  Failed: 2
  Skipped: 0

2 books failed to download, enter 'retry' to retry
```

#### Example 2: Search Multiple Pages and Batch Download

```
# Search pages 1-6 (300 books total)
Z-Lib> searchall semiconductor 6
Starting search: semiconductor (Pages 1 - 6)...
Fetching page 1...
Page 1: Found 50 books
Fetching page 2...
...
Search complete! Found 300 books total

Tip: Enter 'download all' to download all 300 books

Z-Lib> download all
```

#### Example 3: Download Specified Page Range (Skip Already Downloaded Page 1)

```
# Search only pages 2-6
Z-Lib> searchall semiconductor 2-6
Starting search: semiconductor (Pages 2 - 6)...
...
Search complete! Found 250 books

Z-Lib> download all
```

#### Example 4: Retry Failed Downloads

```
Z-Lib> retry
Preparing to retry 5 failed books...
Starting batch download of 5 books (retry)...
```

### Command Line Mode

```bash
# Search books
python zlib_downloader.py -s "Python Programming"

# Search and download all results
python zlib_downloader.py -s "Python Programming" -d all

# Batch download from file
python zlib_downloader.py -f books.txt
```

### Batch Download from File

Create `books.txt`, one book title per line:

```
Python Programming: From Beginner to Practice
Computer Systems: A Programmer's Perspective
Introduction to Algorithms
```

Then run:

```bash
python zlib_downloader.py -f books.txt
```

## Performance Optimization

### Improve Download Speed

Modify `config.py`:

```python
# Reduce request interval
REQUEST_DELAY = 0.3

# Increase concurrency
CONCURRENT_DOWNLOADS = 5
```

### When Network is Unstable

```python
# Increase retry count
MAX_RETRIES = 5

# Increase request interval
REQUEST_DELAY = 1.0

# Reduce concurrency
CONCURRENT_DOWNLOADS = 2
```

## FAQ

### Q: What to do if login fails?

1. Check if email and password are correct
2. Confirm account can log in normally in browser
3. **Manually import cookies** (recommended):
   - Install browser extension [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
   - Export cookies as JSON after logging into Z-Library
   - Save as `cookies.json`
   - Run: `cookies cookies.json`
   - See `export_cookies.md` for details

### Q: Slow download speed?

1. Increase concurrency: `CONCURRENT_DOWNLOADS = 5`
2. Reduce request interval: `REQUEST_DELAY = 0.3`
3. Check if network connection is stable

### Q: Can't find books?

1. Try using English book titles
2. Check network connection
3. Confirm Z-Library website is accessible

### Q: How to handle download failures?

1. Program will automatically retry (default 3 times)
2. Failed books will be recorded, enter `retry` to retry
3. Increase `MAX_RETRIES` value

### Q: Filename encoding issues?

Fixed. The program will automatically:
- Correctly decode UTF-8 filenames
- Remove `(Z-Library)` suffix
- Clean illegal characters

## File Structure

```
ZLibrary-Spider/
├── config.py           # Configuration file
├── zlib_downloader.py  # Main program
├── requirements.txt    # Python dependencies
├── README.md           # Documentation (English)
├── README_CN.md        # Documentation (Chinese)
├── TROUBLESHOOTING.md  # Troubleshooting guide
├── export_cookies.md   # Cookie export guide
├── downloads/          # Download directory
├── cookies.json        # Login state (auto-generated)
└── download_history.json # Download history (auto-generated)
```

## Notes

1. **Use Responsibly**: Comply with website terms of service, do not make excessive requests
2. **Daily Limits**: Program automatically tracks download count
3. **Network Issues**: If unable to access, try configuring proxy
4. **Account Security**: Do not share your cookies file

## Disclaimer

This tool is for educational and research purposes only. Please comply with local laws and regulations and website terms of service. Users are solely responsible for any consequences arising from the use of this tool.

