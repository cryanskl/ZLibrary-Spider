# 故障排除指南

本文档提供常见问题的解决方案。

---

## 🔥 最常见问题

### ❌ 问题 1：遇到 503 错误或"Checking your browser"

#### 症状
```
访问首页: 503
访问登录页面失败: 503
响应内容: Checking your browser...
```

#### 原因
网站启用了 Cloudflare 防护，拦截自动化访问。

#### ✅ 解决方案：导入浏览器 Cookies（推荐）

这是最有效的解决方案！

**步骤：**

1. **安装浏览器扩展**
   - Chrome/Edge: [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
   - Firefox: [Cookie-Editor](https://addons.mozilla.org/firefox/addon/cookie-editor/)

2. **在浏览器中登录 Z-Library**
   - 访问 https://z-library.la 或 https://z-library.ec
   - 使用您的账号登录

3. **导出 Cookies**
   - 点击扩展图标
   - 点击"导出"或"Export"
   - Cookies 会自动复制到剪贴板

4. **保存 Cookies**
   - 创建文件 `browser_cookies.json`
   - 粘贴复制的内容并保存

5. **运行程序并导入**
   ```bash
   ./start.sh
   
   # 在交互模式中输入：
   cookies browser_cookies.json
   
   # 开始使用
   search Python
   download all
   ```

---

### ❌ 问题 2：搜索结果为空（找到 0 本书）

#### 症状
```
正在搜索: Python (第 1 页)...
找到 0 本书
```

#### 可能原因
1. 未导入 cookies 或 cookies 无效
2. 网站 URL 不可用
3. 网络连接问题

#### ✅ 解决方案

**方案 1：导入有效的 Cookies**
```bash
# 确保从可访问的域名导出 cookies
# 在程序中运行：
cookies browser_cookies.json
status  # 检查是否显示"已登录"
```

**方案 2：检查网站是否可访问**
```bash
# 在浏览器中访问以下网址，看哪个能用：
# https://z-library.la
# https://z-library.ec
```

**方案 3：重新导出 Cookies**
- 清除旧的 cookies 文件
- 在浏览器中重新登录
- 导出新的 cookies
- 重新导入到程序

---

### ❌ 问题 3：上周能用，这周 503 了

#### 原因
Z-Library 经常调整防护策略，域名状态会变化：
- 上周：防护较松，程序可直接访问
- 本周：加强了 Cloudflare 保护

#### ✅ 解决方案

**立即可用的方法：**
```bash
# 使用 cookies 导入（100% 有效）
./start.sh
cookies browser_cookies.json
search Python
```

**如果仍然不行：**
1. 等待几小时后重试（防护通常是临时的）
2. 尝试另一个域名（ec 或 la）
3. 使用 VPN 后重试

---

## 🔧 其他常见问题

### ❌ 问题 4：依赖模块未安装

#### 症状
```
ModuleNotFoundError: No module named 'rich'
```

#### 解决方案
```bash
# 确保使用虚拟环境
cd ZLibrary-Spider
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

---

### ❌ 问题 5：下载速度慢

#### 解决方案

编辑 `config.py`：

```python
# 增加并发数量
CONCURRENT_DOWNLOADS = 5  # 从 3 增加到 5

# 减少请求延迟
REQUEST_DELAY = 0.3  # 从 0.5 减少到 0.3

# 注意：设置过高可能触发限制
```

---

### ❌ 问题 6：下载失败频繁

#### 症状
- Connection reset
- Timeout errors
- Incomplete read

#### 解决方案

**方案 1：检查网络**
```bash
# 测试网络连接
ping z-library.la
```

**方案 2：调整超时设置**

编辑 `config.py`：
```python
TIMEOUT = 60  # 增加超时时间（从 30 到 60）
MAX_RETRIES = 5  # 增加重试次数（从 3 到 5）
```

**方案 3：使用重试命令**
```bash
# 在程序中运行
retry  # 重试失败的下载
```

---

### ❌ 问题 7：Cookies 无效或已过期

#### 症状
```
Cookies 导入成功，但未能验证登录状态
```

#### 解决方案

**重新导出 Cookies：**
1. 在浏览器中访问 Z-Library
2. 如果未登录，重新登录
3. 导出新的 cookies
4. 替换旧的 `browser_cookies.json`
5. 重新导入

**注意：** Cookies 通常 1-7 天过期，过期后需要重新导出。

---

### ❌ 问题 8：程序卡住不动

#### 可能原因
- 网络请求超时
- 正在等待响应
- 并发任务过多

#### 解决方案

**按 Ctrl+C 退出，然后：**

1. **降低并发数**
   ```python
   # config.py
   CONCURRENT_DOWNLOADS = 1  # 降低到 1
   ```

2. **增加超时时间**
   ```python
   # config.py
   TIMEOUT = 60  # 增加超时
   ```

3. **检查网络连接**

---

## 📝 使用技巧

### ✅ 最佳实践

1. **定期更新 Cookies**
   - 每周重新导出一次
   - 出现问题时立即重新导出

2. **合理设置参数**
   ```python
   # 推荐配置
   REQUEST_DELAY = 0.5         # 避免太快
   CONCURRENT_DOWNLOADS = 3    # 不要设置太高
   TIMEOUT = 30                # 正常网络下足够
   ```

3. **分批下载**
   - 不要一次下载太多（建议每次 50-100 本）
   - 使用 `download 1-50` 分批下载

4. **保存下载历史**
   - `SKIP_DOWNLOADED = True` 避免重复下载
   - 程序会自动记录已下载的文件

---

## 🆘 仍然无法解决？

### 调试步骤

1. **检查配置**
   ```bash
   # 查看当前配置
   cat config.py | grep -A 2 "BASE_URL"
   ```

2. **查看详细日志**
   ```python
   # config.py
   VERBOSE = True  # 确保已启用详细日志
   ```

3. **测试基本连接**
   ```bash
   # 在浏览器中测试这些网址：
   https://z-library.la
   https://z-library.ec
   ```

4. **检查 cookies 文件**
   ```bash
   # 查看 cookies 文件内容
   cat browser_cookies.json
   # 应该是 JSON 格式的数组
   ```

---

## 💡 预防措施

### 避免常见问题

1. ✅ **始终保持 cookies 最新**
2. ✅ **合理设置并发和延迟**
3. ✅ **分批下载大量文件**
4. ✅ **定期检查网站可用性**
5. ✅ **出现问题立即重新导出 cookies**

### 网站不可用时的应对

**方法 A：等待恢复**
- 通常几小时到一天内会恢复
- 定期重试

**方法 B：重新导出 Cookies**
- 这是最可靠的方法
- 通常能立即解决问题

---

## 📞 获取帮助

如果以上方法都无法解决问题：

1. 查看 `debug_search.html` 文件（如果生成了）
2. 检查是否有错误日志
3. 确认网络连接正常
4. 重新安装依赖：`pip install -r requirements.txt`

---

**记住**：90% 的问题可以通过重新导出并导入 cookies 解决！
