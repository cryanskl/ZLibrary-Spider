# Z-Library 批量下载工具

一个功能强大的 Z-Library 电子书批量下载工具，支持并发下载、多页搜索、断点续传等功能。

## 功能特点

- ✅ **账号登录**：自动登录，保存登录状态
- ✅ **关键词搜索**：支持单页搜索和多页批量搜索
- ✅ **批量下载**：支持单本、多选、范围选择、全部下载
- ✅ **并发下载**：多线程同时下载，大幅提升下载速度
- ✅ **进度显示**：实时显示下载进度和速度
- ✅ **自动重试**：网络错误自动重试，支持手动重试失败项
- ✅ **断点续传**：自动跳过已下载文件
- ✅ **每日限额跟踪**：自动记录下载数量
- ✅ **文件名优化**：自动去除 `(Z-Library)` 后缀
- ✅ **代理支持**：支持 HTTP/HTTPS 代理

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

编辑 `config.py` 文件：

```python
# ============ 账号配置 ============
EMAIL = "your_email@example.com"
PASSWORD = "your_password"

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

### 配置说明

| 配置项 | 说明 | 建议值 |
|--------|------|--------|
| `DAILY_DOWNLOAD_LIMIT` | 每日下载上限 | 根据账号等级设置 |
| `REQUEST_DELAY` | 请求间隔（秒） | 0.3-1.0 |
| `CONCURRENT_DOWNLOADS` | 并发下载数量 | 3-5 |
| `MAX_RETRIES` | 失败重试次数 | 3-5 |

## 使用方法

### 启动程序

```bash
python zlib_downloader.py
```

### 可用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `search <关键词>` | 搜索书籍（仅第1页） | `search Python` |
| `searchall <关键词> [页数]` | 搜索多页 | `searchall Python 6` |
| `searchall <关键词> [起始页-结束页]` | 搜索指定页码范围 | `searchall Python 2-6` |
| `download <序号/范围/all>` | 下载书籍 | `download all` / `download 1-10` / `download 1,3,5` |
| `retry` | 重试失败的下载 | `retry` |
| `login` | 手动登录 | `login` |
| `cookies <文件路径>` | 导入浏览器 cookies | `cookies cookies.json` |
| `status` | 查看当前状态 | `status` |
| `file <文件路径>` | 从文件批量搜索下载 | `file books.txt` |
| `help` | 查看帮助 | `help` |
| `exit` | 退出程序 | `exit` |

### 使用示例

#### 示例 1：搜索并下载所有结果

```
Z-Lib> search 机器学习
正在搜索: 机器学习 (第 1 页)...
找到 50 本书

Z-Lib> download all
开始批量下载 50 本书...
并发数量: 3

总进度 (15/50) ━━━━━━━━━━━━━━━━ 30%
#1 机器学习实战... ━━━━━━━━━━━━━━ 45% 12.5 MB/s
#2 深度学习... ━━━━━━━━━━━━━━━━━━ 23% 8.2 MB/s
#3 统计学习方法... ━━━━━━━━━━━━━ 67% 15.1 MB/s

下载完成！
  成功: 48
  失败: 2
  跳过: 0

有 2 本书下载失败，输入 'retry' 可以重试
```

#### 示例 2：搜索多页并批量下载

```
# 搜索第1-6页（共300本书）
Z-Lib> searchall 半导体 6
开始搜索: 半导体 (第 1 - 6 页)...
正在获取第 1 页...
第 1 页: 找到 50 本书
正在获取第 2 页...
...
搜索完成！共找到 300 本书

提示: 输入 'download all' 下载所有 300 本书

Z-Lib> download all
```

#### 示例 3：下载指定页码范围（跳过已下载的第1页）

```
# 只搜索第2-6页
Z-Lib> searchall 半导体 2-6
开始搜索: 半导体 (第 2 - 6 页)...
...
搜索完成！共找到 250 本书

Z-Lib> download all
```

#### 示例 4：重试失败的下载

```
Z-Lib> retry
准备重试 5 本失败的书籍...
开始批量下载 5 本书 (重试)...
```

### 命令行模式

```bash
# 搜索书籍
python zlib_downloader.py -s "Python编程"

# 搜索并下载所有结果
python zlib_downloader.py -s "Python编程" -d all

# 从文件批量下载
python zlib_downloader.py -f books.txt
```

### 从文件批量下载

创建 `books.txt`，每行一个书名：

```
Python编程从入门到实践
深入理解计算机系统
算法导论
```

然后运行：

```bash
python zlib_downloader.py -f books.txt
```

## 性能优化

### 提升下载速度

修改 `config.py`：

```python
# 减少请求间隔
REQUEST_DELAY = 0.3

# 增加并发数
CONCURRENT_DOWNLOADS = 5
```

### 网络不稳定时

```python
# 增加重试次数
MAX_RETRIES = 5

# 增加请求间隔
REQUEST_DELAY = 1.0

# 减少并发数
CONCURRENT_DOWNLOADS = 2
```

## 常见问题

### Q: 登录失败怎么办？

1. 检查邮箱密码是否正确
2. 在浏览器中确认账号可以正常登录
3. **手动导入 cookies**（推荐）：
   - 安装浏览器扩展 [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
   - 登录 Z-Library 后导出 cookies 为 JSON
   - 保存为 `cookies.json`
   - 运行：`cookies cookies.json`
   - 详见 `export_cookies.md`

### Q: 下载速度慢？

1. 增加并发数：`CONCURRENT_DOWNLOADS = 5`
2. 减少请求间隔：`REQUEST_DELAY = 0.3`
3. 检查网络连接是否稳定

### Q: 搜索不到书籍？

1. 尝试使用英文书名
2. 检查网络连接
3. 确认 Z-Library 网站可访问

### Q: 下载失败后如何处理？

1. 程序会自动重试（默认3次）
2. 失败的书籍会被记录，可输入 `retry` 重试
3. 增加 `MAX_RETRIES` 值

### Q: 文件名乱码？

已修复。程序会自动：
- 正确解码 UTF-8 文件名
- 去除 `(Z-Library)` 后缀
- 清理非法字符

## 文件说明

```
dowload-ZLibrary/
├── config.py           # 配置文件
├── zlib_downloader.py  # 主程序
├── requirements.txt    # Python 依赖
├── README.md           # 使用文档
├── TROUBLESHOOTING.md  # 问题排查记录
├── export_cookies.md   # Cookies 导出指南
├── downloads/          # 下载目录
├── cookies.json        # 登录状态（自动生成）
└── download_history.json # 下载记录（自动生成）
```

## 注意事项

1. **合理使用**：遵守网站使用条款，不要过度请求
2. **每日限额**：程序会自动跟踪下载数量
3. **网络问题**：如无法访问，尝试配置代理
4. **账号安全**：不要分享你的 cookies 文件

## 免责声明

此工具仅供学习交流使用，请遵守当地法律法规和网站使用条款。用户使用本工具所产生的一切后果由用户自行承担。
