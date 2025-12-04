# 开发问题记录

本文档记录了在开发 Z-Library 批量下载工具过程中遇到的问题及解决方案。

---

## 问题 1：依赖模块未安装

### 问题描述
运行程序时报错：
```
ModuleNotFoundError: No module named 'rich'
```

### 原因分析
Python 依赖库未安装，用户直接使用系统 Python 运行程序。

### 解决方案
创建虚拟环境并安装依赖：
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 问题 2：登录失败

### 问题描述
程序显示"登录失败，请检查账号密码"，但在浏览器中可以正常登录。

### 原因分析
1. Z-Library 的登录 API 返回了 `user_id` 和 `user_key`，但代码没有正确识别这个成功响应
2. 登录后需要访问返回的重定向 URL 来设置 cookies

### 解决方案
修改登录逻辑，检测响应中的 `user_id` 和 `user_key`：
```python
# 检查是否有 user_id 和 user_key（登录成功的标志）
if response.get('user_id') and response.get('user_key') and not errors:
    # 访问重定向 URL 来设置 cookies
    redirect_url = response.get('priorityRedirectUrl')
    if redirect_url:
        self.session.get(redirect_url)
    self.is_logged_in = True
    return True
```

---

## 问题 3：搜索返回 0 个结果

### 问题描述
搜索时显示"找到 0 本书"，但在网页上可以搜索到结果。

### 原因分析
1. 服务器返回 Brotli 压缩（`br`）的响应
2. Python `requests` 库默认不支持 Brotli 解压
3. 收到的是压缩后的二进制数据，无法解析

### 解决方案
修改请求头，移除 `br` 压缩支持，只使用 `gzip, deflate`：
```python
self.session.headers.update({
    "Accept-Encoding": "gzip, deflate",  # 移除 br
})
```

---

## 问题 4：搜索结果解析错误

### 问题描述
搜索返回 51 个元素，但只解析出 1 本书（"Create Z-Alert"）。

### 原因分析
Z-Library 使用自定义 HTML 元素 `<z-bookcard>` 显示书籍，而代码使用的是传统的 CSS 选择器。

### 解决方案
分析网页结构后，添加专门解析 `<z-bookcard>` 的方法：
```python
def _parse_z_bookcard(self, card):
    """解析 z-bookcard 元素"""
    book = {}
    book['id'] = card.get('id', '')
    book['url'] = urljoin(self.base_url, card.get('href', ''))
    book['download_url'] = urljoin(self.base_url, card.get('download', ''))
    book['format'] = card.get('extension', '-')
    book['size'] = card.get('filesize', '-')
    
    # 从子元素获取标题和作者
    title_elem = card.find('div', {'slot': 'title'})
    if title_elem:
        book['title'] = title_elem.get_text(strip=True)
    
    author_elem = card.find('div', {'slot': 'author'})
    if author_elem:
        book['author'] = author_elem.get_text(strip=True)
    
    return book
```

---

## 问题 5：下载时网络错误频繁

### 问题描述
下载时频繁出现错误：
- `Connection broken: IncompleteRead`
- `SSLError: EOF occurred in violation of protocol`
- `ProxyError: Remote end closed connection`

### 原因分析
1. 网络不稳定导致连接中断
2. 没有重试机制
3. 超时时间设置不合理

### 解决方案
添加自动重试机制和指数退避：
```python
max_retries = config.MAX_RETRIES
for attempt in range(max_retries):
    try:
        if attempt > 0:
            # 指数退避
            wait_time = config.REQUEST_DELAY * (2 ** attempt)
            time.sleep(wait_time)
        
        resp = self.session.get(download_url, timeout=(10, 90), stream=True)
        # ... 下载逻辑
        
    except (requests.exceptions.ConnectionError, 
            requests.exceptions.Timeout,
            requests.exceptions.SSLError) as e:
        if attempt >= max_retries - 1:
            return False
        # 继续重试
```

同时添加 `retry` 命令，允许手动重试失败的下载。

---

## 问题 6：只能搜索第一页

### 问题描述
用户想下载 300 份文件（6页），但程序只能搜索第一页（50份）。

### 原因分析
搜索功能只实现了单页搜索，没有多页批量搜索功能。

### 解决方案
添加 `search_all_pages` 方法和 `searchall` 命令：
```python
def search_all_pages(self, query, max_pages=10, start_page=1):
    """搜索指定页面范围的书籍"""
    all_books = []
    for page in range(start_page, start_page + max_pages):
        books = self.search(query, page=page)
        if not books:
            break
        all_books.extend(books)
        time.sleep(config.REQUEST_DELAY)
    return all_books
```

支持多种格式：
- `searchall Python` - 搜索第1-10页
- `searchall Python 6` - 搜索第1-6页
- `searchall Python 2-6` - 搜索第2-6页

---

## 问题 7：文件名包含 (Z-Library) 后缀

### 问题描述
下载的文件名都带有 `(Z-Library)` 后缀：
```
核物理与等离子体物理 (Z-Library).pdf
```

### 原因分析
Z-Library 服务器返回的 `Content-Disposition` 头包含这个后缀。

### 解决方案
在保存文件前清理文件名：
```python
if real_filename:
    # 去掉 (Z-Library) 后缀
    real_filename = re.sub(r'\s*\(Z-Library\)\s*', '', real_filename)
    # 清理多余空格
    real_filename = re.sub(r'\s+', ' ', real_filename).strip()
```

---

## 问题 8：文件名乱码

### 问题描述
下载的中文文件名显示为乱码：
```
æ ¸ç©çä¸ç­ç¦»å­½ç©ç.pdf
```

### 原因分析
服务器使用 RFC 5987 格式返回文件名（`filename*=UTF-8''%E4%B8%AD%E6%96%87.pdf`），需要特殊处理。

### 解决方案
正确解析 RFC 5987 格式：
```python
# 优先处理 RFC 5987 格式
rfc5987_match = re.search(r"filename\*=(?:UTF-8|utf-8)''(.+?)(?:;|$)", content_disp)
if rfc5987_match:
    real_filename = rfc5987_match.group(1)
    real_filename = unquote(real_filename, encoding='utf-8')
```

---

## 问题 9：下载速度慢

### 问题描述
批量下载 300 个文件耗时过长。

### 原因分析
1. 请求间隔设置为 2 秒
2. 单线程顺序下载，没有并发

### 解决方案
1. 减少请求间隔：`REQUEST_DELAY = 0.5`
2. 添加并发下载功能：
```python
from concurrent.futures import ThreadPoolExecutor

CONCURRENT_DOWNLOADS = 3  # 同时下载 3 个文件

with ThreadPoolExecutor(max_workers=concurrent) as executor:
    futures = {executor.submit(download_worker, book): book for book in books}
    for future in as_completed(futures):
        future.result()
```

---

## 问题 10：并发下载时没有进度显示

### 问题描述
使用并发下载时，看不到每个文件的下载进度。

### 原因分析
并发模式下禁用了 Rich Progress 进度条，只显示完成提示。

### 解决方案
使用 Rich Progress 的多任务进度显示：
```python
progress = Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    DownloadColumn(),
    TransferSpeedColumn(),
)

# 总进度
overall_task = progress.add_task("总进度", total=len(books))

# 每个并发任务的进度
def download_worker(book, slot_id):
    task_id = progress.add_task(f"#{slot_id} {title}", total=None)
    # ... 下载
    progress.update(overall_task, completed=completed[0])
    progress.remove_task(task_id)
```

---

## 总结

### 主要技术难点

1. **网站反爬机制**：需要正确处理登录、cookies、请求头
2. **动态页面结构**：Z-Library 使用自定义 Web Components（`<z-bookcard>`）
3. **编码问题**：Brotli 压缩、UTF-8 文件名编码
4. **网络稳定性**：需要重试机制和错误处理
5. **性能优化**：并发下载、进度显示

### 关键解决思路

1. **调试输出**：保存 HTML 响应分析页面结构
2. **逐步排查**：先登录、再搜索、再下载，分步解决
3. **容错设计**：重试机制、失败记录、手动重试
4. **用户体验**：进度显示、友好提示、灵活配置

