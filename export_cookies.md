# 如何导出浏览器 Cookies

如果自动登录失败，你可以手动从浏览器导出 cookies 来登录。

## 方法 1: 使用浏览器扩展（推荐）

### Chrome/Edge 浏览器

1. 安装扩展：[EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg) 或 [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)

2. 访问 Z-Library 并登录：https://z-library.la

3. 点击扩展图标，选择"Export"（导出）

4. 选择格式为 **JSON**，复制内容

5. 保存为 `cookies.json` 文件到项目目录

6. 在程序中运行：`cookies cookies.json`

### Firefox 浏览器

1. 安装扩展：[Cookie-Editor](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)

2. 访问 Z-Library 并登录

3. 点击扩展图标，选择"Export"，格式选择 JSON

4. 保存为 `cookies.json`

## 方法 2: 使用开发者工具（手动）

### Chrome/Edge

1. 访问 Z-Library 并登录：https://z-library.la

2. 按 `F12` 打开开发者工具

3. 切换到 **Application** 标签（或 **存储** 标签）

4. 左侧选择 **Cookies** → `https://z-library.la`

5. 右键点击任意 cookie，选择 **Copy all as cURL** 或手动复制所有 cookies

6. 将 cookies 转换为 JSON 格式，保存为 `cookies.json`

### JSON 格式示例

```json
{
  "session": "your_session_value",
  "remember_token": "your_token_value",
  "csrf_token": "your_csrf_value"
}
```

## 方法 3: 使用 Python 脚本（Chrome）

如果你使用 Chrome，可以运行以下脚本自动提取 cookies：

```python
import json
import sqlite3
import os
from pathlib import Path

def get_chrome_cookies(domain="z-library.la"):
    """从 Chrome 提取 cookies"""
    # Chrome cookies 路径
    chrome_path = Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies"
    
    if not chrome_path.exists():
        print("未找到 Chrome cookies 文件")
        return None
    
    # 复制 cookies 文件（因为 Chrome 会锁定数据库）
    import shutil
    temp_db = "/tmp/chrome_cookies.db"
    shutil.copy2(chrome_path, temp_db)
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    cookies = {}
    cursor.execute(
        "SELECT name, value FROM cookies WHERE host_key LIKE ?",
        (f"%{domain}%",)
    )
    
    for name, value in cursor.fetchall():
        cookies[name] = value
    
    conn.close()
    os.remove(temp_db)
    
    return cookies

if __name__ == "__main__":
    cookies = get_chrome_cookies()
    if cookies:
        with open("cookies.json", "w") as f:
            json.dump(cookies, f, indent=2)
        print("Cookies 已导出到 cookies.json")
    else:
        print("未找到 cookies")
```

## 使用导出的 Cookies

在交互模式中：

```
Z-Lib> cookies cookies.json
```

或者在代码中：

```python
from zlib_downloader import ZLibraryDownloader

downloader = ZLibraryDownloader()
downloader.import_cookies_from_file("cookies.json")
```

## 注意事项

- Cookies 有时效性，过期后需要重新导出
- 确保 cookies 文件格式正确（JSON）
- 不要分享你的 cookies 文件，它包含你的登录凭证

