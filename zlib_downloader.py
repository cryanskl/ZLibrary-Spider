#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Z-Library 批量下载工具
支持搜索、批量下载、断点续传等功能
"""

import os
import re
import sys
import json
import time
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, date
from urllib.parse import urljoin, quote
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TaskID
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.live import Live

import config

console = Console()


class ZLibraryDownloader:
    """Z-Library 下载器类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })
        
        if config.USE_PROXY:
            self.session.proxies = config.PROXY
        
        self.base_url = config.BASE_URL
        self.is_logged_in = False
        self.download_count_today = 0
        self.download_history = self._load_download_history()
        
        # 创建下载目录
        Path(config.DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
        
        # 尝试加载已保存的 cookies
        self._load_cookies()
    
    def _load_cookies(self):
        """加载保存的 cookies"""
        if os.path.exists(config.COOKIES_FILE):
            try:
                with open(config.COOKIES_FILE, 'r') as f:
                    cookies = json.load(f)
                    self.session.cookies.update(cookies)
                    console.print("[green]已加载保存的登录状态[/green]")
            except Exception as e:
                console.print(f"[yellow]加载 cookies 失败: {e}[/yellow]")
    
    def _save_cookies(self):
        """保存 cookies"""
        try:
            cookies = dict(self.session.cookies)
            with open(config.COOKIES_FILE, 'w') as f:
                json.dump(cookies, f)
        except Exception as e:
            console.print(f"[yellow]保存 cookies 失败: {e}[/yellow]")
    
    def _load_download_history(self):
        """加载下载历史"""
        if os.path.exists(config.DOWNLOAD_HISTORY_FILE):
            try:
                with open(config.DOWNLOAD_HISTORY_FILE, 'r') as f:
                    data = json.load(f)
                    # 检查今日下载数量
                    if data.get('date') == str(date.today()):
                        self.download_count_today = data.get('count_today', 0)
                    return data.get('downloaded', [])
            except Exception:
                pass
        return []
    
    def _save_download_history(self):
        """保存下载历史"""
        try:
            data = {
                'date': str(date.today()),
                'count_today': self.download_count_today,
                'downloaded': self.download_history
            }
            with open(config.DOWNLOAD_HISTORY_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            console.print(f"[yellow]保存下载历史失败: {e}[/yellow]")
    
    def login(self, email=None, password=None):
        """登录 Z-Library"""
        email = email or config.EMAIL
        password = password or config.PASSWORD
        
        if email == "your_email@example.com":
            console.print("[red]请先在 config.py 中配置你的邮箱和密码！[/red]")
            return False
        
        console.print("[cyan]正在登录 Z-Library...[/cyan]")
        
        try:
            # 首先访问首页获取 cookies
            home_url = self.base_url
            resp = self.session.get(home_url, timeout=config.TIMEOUT)
            if config.VERBOSE:
                console.print(f"[dim]访问首页: {resp.status_code}[/dim]")
            
            # 访问登录页面获取必要的 token
            login_page_url = urljoin(self.base_url, "/login")
            resp = self.session.get(login_page_url, timeout=config.TIMEOUT)
            
            if resp.status_code != 200:
                console.print(f"[red]访问登录页面失败: {resp.status_code}[/red]")
                if config.VERBOSE:
                    console.print(f"[dim]响应内容: {resp.text[:500]}[/dim]")
                return False
            
            # 解析登录表单
            soup = BeautifulSoup(resp.text, 'lxml')
            
            # 查找 CSRF token（尝试多种可能的名称）
            csrf_token = ""
            for token_name in ['_token', 'csrf_token', 'csrf', 'token']:
                token_input = soup.find('input', {'name': token_name})
                if token_input:
                    csrf_token = token_input.get('value', '')
                    if csrf_token:
                        if config.VERBOSE:
                            console.print(f"[dim]找到 CSRF token: {token_name}[/dim]")
                        break
            
            # 查找表单 action URL
            form = soup.find('form', {'method': 'post'}) or soup.find('form')
            form_action = ""
            if form and form.get('action'):
                form_action = form.get('action')
            
            # 尝试多种登录端点
            login_endpoints = [
                urljoin(self.base_url, form_action) if form_action else None,
                urljoin(self.base_url, "/rpc.php"),
                urljoin(self.base_url, "/login"),
                urljoin(self.base_url, "/api/login"),
            ]
            
            login_endpoints = [e for e in login_endpoints if e]
            
            for login_url in login_endpoints:
                if config.VERBOSE:
                    console.print(f"[dim]尝试登录端点: {login_url}[/dim]")
                
                # 方法1: 使用 rpc.php (AJAX 方式)
                login_data = {
                    "email": email,
                    "password": password,
                }
                
                if "rpc.php" in login_url:
                    login_data.update({
                        "isModal": "true",
                        "action": "login",
                        "redirectUrl": "",
                        "gg_json_mode": "1"
                    })
                
                if csrf_token:
                    login_data['_token'] = csrf_token
                
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "X-Requested-With": "XMLHttpRequest",
                    "Origin": self.base_url,
                    "Referer": login_page_url
                }
                
                resp = self.session.post(login_url, data=login_data, headers=headers, timeout=config.TIMEOUT, allow_redirects=False)
                
                if config.VERBOSE:
                    console.print(f"[dim]登录响应状态: {resp.status_code}[/dim]")
                    console.print(f"[dim]响应头 Location: {resp.headers.get('Location', 'None')}[/dim]")
                    if resp.text:
                        console.print(f"[dim]响应内容: {resp.text[:300]}[/dim]")
                
                # 检查是否重定向（通常登录成功会重定向）
                if resp.status_code in [302, 301]:
                    location = resp.headers.get('Location', '')
                    if location and 'login' not in location.lower():
                        # 可能是登录成功
                        if self._check_login_status():
                            self.is_logged_in = True
                            self._save_cookies()
                            console.print("[green]✓ 登录成功！[/green]")
                            return True
                
                # 检查 JSON 响应
                if resp.status_code == 200:
                    try:
                        result = resp.json()
                        if config.VERBOSE:
                            console.print(f"[dim]JSON 响应: {result}[/dim]")
                        
                        # 检查错误信息
                        if isinstance(result, dict):
                            if result.get('response', {}).get('validationError'):
                                error_msg = result['response']['validationError']
                                console.print(f"[red]登录失败: {error_msg}[/red]")
                                continue
                            
                            # Z-Library 成功响应格式: {"errors":[], "response":{"user_id":..., "user_key":...}}
                            response = result.get('response', {})
                            errors = result.get('errors', [])
                            
                            # 检查是否有 user_id 和 user_key（登录成功的标志）
                            if response.get('user_id') and response.get('user_key') and not errors:
                                console.print(f"[green]✓ 登录成功！用户ID: {response.get('user_id')}[/green]")
                                
                                # 访问重定向 URL 来设置 cookies
                                redirect_url = response.get('priorityRedirectUrl') or response.get('forceRedirection')
                                if redirect_url:
                                    redirect_url = urljoin(self.base_url, redirect_url)
                                    if config.VERBOSE:
                                        console.print(f"[dim]访问重定向 URL: {redirect_url}[/dim]")
                                    self.session.get(redirect_url, timeout=config.TIMEOUT)
                                
                                # 直接标记为登录成功（因为已经收到有效的 user_id 和 user_key）
                                self.is_logged_in = True
                                self._save_cookies()
                                return True
                            
                            # 检查其他成功标志
                            if result.get('status') == 'success' or result.get('success') or result.get('logged_in'):
                                if self._check_login_status():
                                    self.is_logged_in = True
                                    self._save_cookies()
                                    console.print("[green]✓ 登录成功！[/green]")
                                    return True
                    except (json.JSONDecodeError, ValueError):
                        # 不是 JSON，可能是 HTML
                        if 'logout' in resp.text.lower() or 'profile' in resp.text.lower():
                            if self._check_login_status():
                                self.is_logged_in = True
                                self._save_cookies()
                                console.print("[green]✓ 登录成功！[/green]")
                                return True
            # 所有方法都失败，最后验证一次登录状态
            if self._check_login_status():
                self.is_logged_in = True
                self._save_cookies()
                console.print("[green]✓ 登录成功！[/green]")
                return True
            
            console.print("[red]登录失败，请检查账号密码[/red]")
            if config.VERBOSE:
                console.print("[yellow]提示: 如果网页能正常登录，可能是网站更新了登录机制，需要手动导出 cookies[/yellow]")
            return False
            
        except Exception as e:
            console.print(f"[red]登录出错: {e}[/red]")
            if config.VERBOSE:
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
            return False
    
    def _check_login_status(self):
        """检查是否已登录"""
        try:
            # 方法1: 访问个人页面检查登录状态
            profile_url = urljoin(self.base_url, "/profile")
            resp = self.session.get(profile_url, timeout=config.TIMEOUT, allow_redirects=False)
            
            # 如果被重定向到登录页面，说明未登录
            if resp.status_code == 302:
                location = resp.headers.get('Location', '')
                if 'login' in location.lower():
                    return False
            
            # 检查页面内容
            if resp.status_code == 200:
                text_lower = resp.text.lower()
                # 检查登录成功的标志
                if any(keyword in text_lower for keyword in ['logout', 'profile', 'my books', 'downloads', 'settings']):
                    # 确保没有登录表单
                    if 'login' not in text_lower or 'sign in' not in text_lower:
                        self.is_logged_in = True
                        return True
            
            # 方法2: 访问首页检查是否有用户信息
            home_resp = self.session.get(self.base_url, timeout=config.TIMEOUT)
            if home_resp.status_code == 200:
                text_lower = home_resp.text.lower()
                if 'logout' in text_lower or 'my profile' in text_lower:
                    self.is_logged_in = True
                    return True
            
            return False
        except Exception as e:
            if config.VERBOSE:
                console.print(f"[dim]检查登录状态出错: {e}[/dim]")
            return False
    
    def import_cookies_from_browser(self, cookies_dict):
        """从浏览器导入 cookies（手动方式）"""
        try:
            self.session.cookies.update(cookies_dict)
            self._save_cookies()
            if self._check_login_status():
                self.is_logged_in = True
                console.print("[green]✓ 通过 cookies 登录成功！[/green]")
                return True
            else:
                console.print("[yellow]Cookies 无效或已过期[/yellow]")
                return False
        except Exception as e:
            console.print(f"[red]导入 cookies 失败: {e}[/red]")
            return False
    
    def import_cookies_from_file(self, filepath):
        """从文件导入 cookies"""
        try:
            with open(filepath, 'r') as f:
                cookies = json.load(f)
                return self.import_cookies_from_browser(cookies)
        except Exception as e:
            console.print(f"[red]读取 cookies 文件失败: {e}[/red]")
            return False
    
    def search(self, query, page=1, exact_match=False):
        """搜索书籍"""
        console.print(f"[cyan]正在搜索: {query} (第 {page} 页)...[/cyan]")
        
        try:
            search_url = urljoin(self.base_url, "/s/")
            params = {
                "q": query,
                "page": page
            }
            if exact_match:
                params["e"] = 1
            
            resp = self.session.get(search_url, params=params, timeout=config.TIMEOUT)
            
            if resp.status_code != 200:
                console.print(f"[red]搜索失败: {resp.status_code}[/red]")
                return []
            
            # 调试: 保存搜索结果 HTML
            if config.VERBOSE:
                debug_file = "debug_search.html"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(resp.text)
                console.print(f"[dim]已保存搜索结果到 {debug_file}[/dim]")
            
            soup = BeautifulSoup(resp.text, 'lxml')
            books = []
            
            # Z-Library 使用 <z-bookcard> 自定义元素显示书籍
            book_cards = soup.find_all('z-bookcard')
            if config.VERBOSE:
                console.print(f"[dim]找到 {len(book_cards)} 个 z-bookcard 元素[/dim]")
            
            for card in book_cards:
                try:
                    book = self._parse_z_bookcard(card)
                    if book:
                        books.append(book)
                except Exception as e:
                    if config.VERBOSE:
                        console.print(f"[yellow]解析书籍失败: {e}[/yellow]")
            
            console.print(f"[green]找到 {len(books)} 本书[/green]")
            return books
            
        except Exception as e:
            console.print(f"[red]搜索出错: {e}[/red]")
            if config.VERBOSE:
                import traceback
    
    def search_all_pages(self, query, max_pages=10, start_page=1, exact_match=False):
        """搜索指定页面范围的书籍"""
        all_books = []
        page = start_page
        end_page = start_page + max_pages - 1
        
        console.print(f"[cyan]开始搜索: {query} (第 {start_page} - {end_page} 页)...[/cyan]")
        
        while page <= end_page:
            console.print(f"[dim]正在获取第 {page} 页...[/dim]")
            
            try:
                search_url = urljoin(self.base_url, "/s/")
                params = {
                    "q": query,
                    "page": page
                }
                if exact_match:
                    params["e"] = 1
                
                resp = self.session.get(search_url, params=params, timeout=config.TIMEOUT)
                
                if resp.status_code != 200:
                    console.print(f"[yellow]第 {page} 页获取失败: {resp.status_code}[/yellow]")
                    break
                
                soup = BeautifulSoup(resp.text, 'lxml')
                book_cards = soup.find_all('z-bookcard')
                
                if not book_cards:
                    console.print(f"[dim]第 {page} 页没有更多结果，搜索完成[/dim]")
                    break
                
                for card in book_cards:
                    try:
                        book = self._parse_z_bookcard(card)
                        if book:
                            all_books.append(book)
                    except Exception:
                        pass
                
                console.print(f"[green]第 {page} 页: 找到 {len(book_cards)} 本书[/green]")
                page += 1
                
                # 延迟避免请求过快
                time.sleep(config.REQUEST_DELAY)
                
            except Exception as e:
                console.print(f"[red]第 {page} 页搜索出错: {e}[/red]")
                break
        
        console.print(f"\n[bold green]搜索完成！共找到 {len(all_books)} 本书[/bold green]")
        return all_books
    
    def _parse_z_bookcard(self, card):
        """解析 z-bookcard 元素（Z-Library 专用）"""
        book = {}
        
        # 从属性获取信息
        book_id = card.get('id', '')
        href = card.get('href', '')
        download = card.get('download', '')
        
        if book_id:
            book['id'] = book_id
        
        if href:
            book['url'] = urljoin(self.base_url, href)
        
        if download:
            book['download_url'] = urljoin(self.base_url, download)
        
        # 获取文件格式和大小
        book['format'] = card.get('extension', '-')
        book['size'] = card.get('filesize', '-')
        book['language'] = card.get('language', '')
        book['year'] = card.get('year', '')
        
        # 从子元素获取标题和作者
        title_elem = card.find('div', {'slot': 'title'})
        if title_elem:
            book['title'] = title_elem.get_text(strip=True)
        
        author_elem = card.find('div', {'slot': 'author'})
        if author_elem:
            book['author'] = author_elem.get_text(strip=True)
        else:
            book['author'] = "Unknown"
        
        # 确保有标题和URL
        if book.get('title') and book.get('url'):
            return book
        return None
    
    def _parse_book_item(self, item):
        """解析书籍条目（旧版备用）"""
        book = {}
        
        # 获取链接
        link = item.find('a', href=True)
        if link:
            book['url'] = urljoin(self.base_url, link['href'])
            book['id'] = link['href'].split('/')[-1] if '/' in link['href'] else link['href']
        
        # 获取标题
        title_elem = item.find(['h3', 'h4', 'a'], class_=lambda x: x and 'title' in x.lower() if x else False)
        if not title_elem:
            title_elem = item.find('a')
        if title_elem:
            book['title'] = title_elem.get_text(strip=True)
        
        # 获取作者
        author_elem = item.find(class_=lambda x: x and 'author' in x.lower() if x else False)
        if author_elem:
            book['author'] = author_elem.get_text(strip=True)
        else:
            book['author'] = "Unknown"
        
        # 获取格式和大小
        property_elem = item.find(class_=lambda x: x and ('property' in x.lower() or 'format' in x.lower()) if x else False)
        if property_elem:
            text = property_elem.get_text(strip=True)
            # 尝试提取格式
            format_match = re.search(r'\b(pdf|epub|mobi|azw3|fb2|djvu|txt|doc|docx)\b', text, re.I)
            if format_match:
                book['format'] = format_match.group(1).lower()
            # 尝试提取大小
            size_match = re.search(r'(\d+(?:\.\d+)?\s*(?:KB|MB|GB))', text, re.I)
            if size_match:
                book['size'] = size_match.group(1)
        
        if 'title' in book and 'url' in book:
            return book
        return None
    
    def _parse_book_item_alt(self, item):
        """备用的书籍条目解析方法"""
        book = {}
        
        # 尝试从各种属性获取信息
        link = item.find('a', href=True)
        if link:
            book['url'] = urljoin(self.base_url, link['href'])
            book['id'] = link['href'].split('/')[-1]
        
        # 获取标题
        for selector in ['h3', 'h4', '.title', '[itemprop="name"]', 'a']:
            elem = item.find(selector)
            if elem and elem.get_text(strip=True):
                book['title'] = elem.get_text(strip=True)
                break
        
        book['author'] = "Unknown"
        book['format'] = "unknown"
        
        if 'title' in book and 'url' in book:
            return book
        return None
    
    def get_book_details(self, book_url):
        """获取书籍详情页信息"""
        try:
            time.sleep(config.REQUEST_DELAY)
            resp = self.session.get(book_url, timeout=config.TIMEOUT)
            
            if resp.status_code != 200:
                return None
            
            soup = BeautifulSoup(resp.text, 'lxml')
            details = {'url': book_url}
            
            # 获取标题
            title_elem = soup.find('h1') or soup.find(class_='book-title')
            if title_elem:
                details['title'] = title_elem.get_text(strip=True)
            
            # 获取下载链接
            download_btn = soup.find('a', class_=lambda x: x and 'download' in x.lower() if x else False)
            if not download_btn:
                download_btn = soup.find('a', href=lambda x: x and '/dl/' in x if x else False)
            if not download_btn:
                download_btn = soup.select_one('a[href*="download"], a.btn-download, .download-btn a')
            
            if download_btn:
                details['download_url'] = urljoin(self.base_url, download_btn.get('href', ''))
            
            # 获取文件信息
            for prop in soup.find_all(class_=lambda x: x and 'property' in x.lower() if x else False):
                text = prop.get_text(strip=True).lower()
                if 'format' in text or 'type' in text:
                    format_match = re.search(r'(pdf|epub|mobi|azw3|fb2|djvu)', text)
                    if format_match:
                        details['format'] = format_match.group(1)
                if 'size' in text or any(unit in text for unit in ['kb', 'mb', 'gb']):
                    size_match = re.search(r'(\d+(?:\.\d+)?\s*(?:KB|MB|GB))', text, re.I)
                    if size_match:
                        details['size'] = size_match.group(1)
            
            return details
            
        except Exception as e:
            if config.VERBOSE:
                console.print(f"[yellow]获取详情失败: {e}[/yellow]")
            return None
    
    def download_book(self, book, progress=None, task_id=None):
        """下载单本书籍"""
        if self.download_count_today >= config.DAILY_DOWNLOAD_LIMIT:
            console.print("[yellow]已达到今日下载上限！[/yellow]")
            return False
        
        book_id = book.get('id', book.get('url', ''))
        
        # 优先使用搜索结果中的下载链接（来自 z-bookcard）
        download_url = book.get('download_url')
        title = book.get('title', 'Unknown')
        file_format = book.get('format', 'pdf')
        
        # 如果搜索结果没有下载链接，则访问详情页获取
        if not download_url:
            details = self.get_book_details(book['url'])
            if not details or 'download_url' not in details:
                console.print(f"[red]无法获取下载链接: {book.get('title', 'Unknown')}[/red]")
                return False
            download_url = details['download_url']
            title = details.get('title', title)
            file_format = details.get('format', file_format)
        
        # 清理文件名
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)[:100]
        filename = f"{safe_title}.{file_format}"
        filepath = os.path.join(config.DOWNLOAD_DIR, filename)
        
        # 带重试的下载
        max_retries = config.MAX_RETRIES
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    # 重试前等待，指数退避
                    wait_time = config.REQUEST_DELAY * (2 ** attempt)
                    console.print(f"[yellow]第 {attempt + 1} 次重试，等待 {wait_time} 秒...[/yellow]")
                    time.sleep(wait_time)
                else:
                    time.sleep(config.REQUEST_DELAY)
                
                # 下载文件
                resp = self.session.get(
                    download_url, 
                    timeout=(10, config.TIMEOUT * 3),  # (连接超时, 读取超时)
                    stream=True,
                    allow_redirects=True
                )
                
                if resp.status_code != 200:
                    console.print(f"[red]下载失败 ({resp.status_code}): {title}[/red]")
                    if attempt < max_retries - 1:
                        continue
                    return False
                
                # 获取文件大小
                total_size = int(resp.headers.get('content-length', 0))
                
                # 从响应头获取真实文件名
                content_disp = resp.headers.get('content-disposition', '')
                real_filename = None
                
                if content_disp:
                    # 优先处理 RFC 5987 格式: filename*=UTF-8''%E4%B8%AD%E6%96%87.pdf
                    rfc5987_match = re.search(r"filename\*=(?:UTF-8|utf-8)''(.+?)(?:;|$)", content_disp)
                    if rfc5987_match:
                        real_filename = rfc5987_match.group(1)
                        try:
                            from urllib.parse import unquote
                            real_filename = unquote(real_filename, encoding='utf-8')
                        except:
                            pass
                    
                    # 备用: 普通 filename= 格式
                    if not real_filename:
                        fname_match = re.search(r'filename=["\']?([^"\';\n]+)', content_disp)
                        if fname_match:
                            real_filename = fname_match.group(1).strip('"\'')
                            try:
                                from urllib.parse import unquote
                                real_filename = unquote(real_filename, encoding='utf-8')
                            except:
                                pass
                
                # 如果成功获取文件名，使用它
                if real_filename:
                    # 去掉 (Z-Library) 后缀
                    real_filename = re.sub(r'\s*\(Z-Library\)\s*', '', real_filename)
                    # 清理多余空格
                    real_filename = re.sub(r'\s+', ' ', real_filename).strip()
                    # 清理非法字符
                    real_filename = re.sub(r'[<>:"/\\|?*]', '_', real_filename)
                    filepath = os.path.join(config.DOWNLOAD_DIR, real_filename)
                
                # 确保下载目录存在
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # 写入临时文件
                temp_filepath = filepath + '.tmp'
                downloaded_size = 0
                
                with open(temp_filepath, 'wb') as f:
                    if progress and task_id is not None:
                        progress.update(task_id, total=total_size)
                        for chunk in resp.iter_content(chunk_size=32768):
                            if chunk:
                                f.write(chunk)
                                downloaded_size += len(chunk)
                                progress.update(task_id, advance=len(chunk))
                    else:
                        for chunk in resp.iter_content(chunk_size=32768):
                            if chunk:
                                f.write(chunk)
                                downloaded_size += len(chunk)
                
                # 验证下载完整性
                if total_size > 0 and downloaded_size < total_size:
                    raise Exception(f"下载不完整: {downloaded_size}/{total_size} bytes")
                
                # 重命名临时文件为正式文件
                if os.path.exists(filepath):
                    os.remove(filepath)
                os.rename(temp_filepath, filepath)
                
                self.download_count_today += 1
                self.download_history.append(book_id)
                self._save_download_history()
                
                console.print(f"[green]✓ 下载完成: {os.path.basename(filepath)}[/green]")
                return True
                
            except (requests.exceptions.ConnectionError, 
                    requests.exceptions.Timeout,
                    requests.exceptions.ChunkedEncodingError,
                    requests.exceptions.SSLError) as e:
                error_msg = str(e)[:100]
                console.print(f"[yellow]网络错误 (尝试 {attempt + 1}/{max_retries}): {error_msg}[/yellow]")
                # 删除不完整的临时文件
                temp_filepath = filepath + '.tmp'
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                if attempt >= max_retries - 1:
                    console.print(f"[red]下载失败，已重试 {max_retries} 次: {title}[/red]")
                    return False
                    
            except Exception as e:
                console.print(f"[red]下载出错: {e}[/red]")
                # 删除不完整的文件
                temp_filepath = filepath + '.tmp'
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                if os.path.exists(filepath):
                    os.remove(filepath)
                if attempt >= max_retries - 1:
                    return False
        
        return False
    
    def batch_download(self, books, is_retry=False):
        """批量下载书籍（支持并发下载）"""
        if not books:
            console.print("[yellow]没有可下载的书籍[/yellow]")
            return []
        
        total = len(books)
        success = 0
        failed = 0
        skipped = 0
        failed_books = []  # 记录失败的书籍
        
        # 线程安全的计数器
        lock = threading.Lock()
        completed = [0]  # 使用列表以便在闭包中修改
        
        # 获取并发数量
        concurrent = getattr(config, 'CONCURRENT_DOWNLOADS', 1)
        
        retry_msg = " (重试)" if is_retry else ""
        console.print(f"\n[cyan]开始批量下载 {total} 本书{retry_msg}...[/cyan]")
        console.print(f"[dim]今日已下载: {self.download_count_today}/{config.DAILY_DOWNLOAD_LIMIT}[/dim]")
        console.print(f"[dim]并发数量: {concurrent}[/dim]\n")
        
        # 过滤掉超过每日限额的书籍
        remaining_quota = config.DAILY_DOWNLOAD_LIMIT - self.download_count_today
        if remaining_quota < total:
            console.print(f"[yellow]今日剩余配额 {remaining_quota}，将只下载前 {remaining_quota} 本[/yellow]")
            books_to_download = books[:remaining_quota]
            skipped = total - remaining_quota
        else:
            books_to_download = books
        
        # 创建进度条
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            DownloadColumn(),
            TransferSpeedColumn(),
            console=console,
            refresh_per_second=4
        )
        
        # 总进度任务
        overall_task = progress.add_task(
            f"[cyan]总进度 (0/{len(books_to_download)})[/cyan]", 
            total=len(books_to_download)
        )
        
        # 存储每个并发任务的进度 ID
        task_slots = {}  # slot_id -> (task_id, book_title)
        
        def download_worker(book, index, slot_id):
            """下载工作线程"""
            nonlocal success, failed
            
            # 检查是否达到限制
            with lock:
                if self.download_count_today >= config.DAILY_DOWNLOAD_LIMIT:
                    return None
            
            title = book.get('title', 'Unknown')[:35]
            
            # 更新任务描述
            with lock:
                task_id = progress.add_task(f"[yellow]#{slot_id+1} {title}...[/yellow]", total=None)
                task_slots[slot_id] = task_id
            
            result = self.download_book(book, progress=None, task_id=None)
            
            with lock:
                completed[0] += 1
                progress.update(overall_task, 
                    completed=completed[0],
                    description=f"[cyan]总进度 ({completed[0]}/{len(books_to_download)})[/cyan]"
                )
                
                # 移除该任务的进度
                if slot_id in task_slots:
                    progress.remove_task(task_slots[slot_id])
                    del task_slots[slot_id]
                
                if result:
                    success += 1
                else:
                    failed += 1
                    failed_books.append(book)
            
            return result
        
        # 使用进度条包装下载
        with progress:
            if concurrent > 1:
                # 并发下载
                with ThreadPoolExecutor(max_workers=concurrent) as executor:
                    futures = {}
                    for i, book in enumerate(books_to_download):
                        slot_id = i % concurrent
                        future = executor.submit(download_worker, book, i, slot_id)
                        futures[future] = book
                    
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as e:
                            with lock:
                                completed[0] += 1
                                failed += 1
                                failed_books.append(futures[future])
                                progress.update(overall_task, completed=completed[0])
            else:
                # 单线程顺序下载
                for i, book in enumerate(books_to_download):
                    download_worker(book, i, 0)
        
        # 打印统计
        console.print(f"\n[bold]下载完成！[/bold]")
        console.print(f"  [green]成功: {success}[/green]")
        console.print(f"  [red]失败: {failed}[/red]")
        console.print(f"  [yellow]跳过: {skipped}[/yellow]")
        console.print(f"  [dim]今日总计: {self.download_count_today}/{config.DAILY_DOWNLOAD_LIMIT}[/dim]")
        
        # 保存失败列表供重试
        self.last_failed_books = failed_books
        
        # 如果有失败的，提示可以重试
        if failed_books and not is_retry:
            console.print(f"\n[yellow]有 {len(failed_books)} 本书下载失败，输入 'retry' 可以重试[/yellow]")
        
        return failed_books
    
    def display_books(self, books):
        """以表格形式显示书籍列表"""
        if not books:
            console.print("[yellow]没有找到书籍[/yellow]")
            return
        
        table = Table(title="搜索结果", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("标题", style="cyan", max_width=50)
        table.add_column("作者", style="green", max_width=20)
        table.add_column("格式", style="yellow", width=8)
        table.add_column("大小", style="blue", width=10)
        
        for i, book in enumerate(books, 1):
            table.add_row(
                str(i),
                book.get('title', 'Unknown')[:50],
                book.get('author', 'Unknown')[:20],
                book.get('format', '-'),
                book.get('size', '-')
            )
        
        console.print(table)
    
    def search_and_download_from_file(self, filepath):
        """从文件读取书名列表并批量搜索下载"""
        if not os.path.exists(filepath):
            console.print(f"[red]文件不存在: {filepath}[/red]")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            queries = [line.strip() for line in f if line.strip()]
        
        console.print(f"[cyan]从文件读取了 {len(queries)} 个搜索关键词[/cyan]\n")
        
        all_books = []
        for query in queries:
            books = self.search(query)
            if books:
                # 只取每个搜索结果的第一本（最相关的）
                all_books.append(books[0])
            time.sleep(config.REQUEST_DELAY)
        
        if all_books:
            console.print(f"\n[green]共找到 {len(all_books)} 本书[/green]")
            if Confirm.ask("是否开始下载？"):
                self.batch_download(all_books)
        else:
            console.print("[yellow]没有找到任何书籍[/yellow]")


def interactive_mode(downloader):
    """交互模式"""
    console.print(Panel.fit(
        "[bold cyan]Z-Library 批量下载工具[/bold cyan]\n"
        "[dim]输入 help 查看帮助[/dim]",
        border_style="cyan"
    ))
    
    while True:
        try:
            cmd = Prompt.ask("\n[bold green]Z-Lib[/bold green]").strip()
            
            if not cmd:
                continue
            
            if cmd.lower() in ['exit', 'quit', 'q']:
                console.print("[dim]再见！[/dim]")
                break
            
            elif cmd.lower() == 'help':
                console.print("""
[bold]可用命令:[/bold]
  [cyan]search <关键词>[/cyan]      - 搜索书籍（仅第1页）
  [cyan]searchall <关键词> [起始页-结束页][/cyan] - 搜索指定页面范围
                           例: searchall Python      (搜索第1-10页)
                           例: searchall Python 6    (搜索第1-6页)
                           例: searchall Python 2-6  (搜索第2-6页)
  [cyan]download <序号/all>[/cyan]  - 下载书籍（如: download all, download 1-10）
  [cyan]retry[/cyan]                - 重试失败的下载
  [cyan]login[/cyan]                - 登录账号
  [cyan]cookies <文件路径>[/cyan]   - 从文件导入浏览器 cookies（如果自动登录失败）
  [cyan]status[/cyan]           - 查看状态
  [cyan]download <序号>[/cyan]  - 下载指定书籍 (如: download 1,2,3 或 download 1-5 或 download all)
  [cyan]file <文件路径>[/cyan]  - 从文件批量搜索下载
  [cyan]exit[/cyan]             - 退出程序
                """)
            
            elif cmd.lower() == 'login':
                email = Prompt.ask("邮箱")
                password = Prompt.ask("密码", password=True)
                downloader.login(email, password)
            
            elif cmd.lower().startswith('cookies '):
                filepath = cmd[8:].strip()
                if filepath:
                    downloader.import_cookies_from_file(filepath)
                else:
                    console.print("[yellow]请提供 cookies 文件路径[/yellow]")
                    console.print("[dim]提示: 使用浏览器扩展（如 EditThisCookie）导出 cookies 为 JSON 格式[/dim]")
            
            elif cmd.lower() == 'status':
                status = "已登录" if downloader.is_logged_in else "未登录"
                console.print(f"""
[bold]状态信息:[/bold]
  登录状态: {status}
  今日下载: {downloader.download_count_today}/{config.DAILY_DOWNLOAD_LIMIT}
  下载目录: {config.DOWNLOAD_DIR}
                """)
            
            elif cmd.lower().startswith('searchall '):
                # 搜索指定页面范围: searchall <关键词> [页数] 或 searchall <关键词> [起始页-结束页]
                parts = cmd[10:].strip().split()
                if not parts:
                    console.print("[yellow]请提供搜索关键词[/yellow]")
                    continue
                
                # 默认值
                start_page = 1
                max_pages = 10
                
                # 检查最后一个参数
                if len(parts) >= 2:
                    last_part = parts[-1]
                    if '-' in last_part and last_part.replace('-', '').isdigit():
                        # 格式: 2-6 (起始页-结束页)
                        try:
                            start_page, end_page = map(int, last_part.split('-'))
                            max_pages = end_page - start_page + 1
                            query = ' '.join(parts[:-1])
                        except:
                            query = ' '.join(parts)
                    elif last_part.isdigit():
                        # 格式: 6 (仅页数，从第1页开始)
                        max_pages = int(last_part)
                        query = ' '.join(parts[:-1])
                    else:
                        query = ' '.join(parts)
                else:
                    query = ' '.join(parts)
                
                books = downloader.search_all_pages(query, max_pages=max_pages, start_page=start_page)
                downloader.display_books(books)
                downloader.last_search_results = books
                
                if books:
                    console.print(f"\n[dim]提示: 输入 'download all' 下载所有 {len(books)} 本书[/dim]")
            
            elif cmd.lower().startswith('search '):
                query = cmd[7:].strip()
                if query:
                    books = downloader.search(query)
                    downloader.display_books(books)
                    # 保存最近搜索结果供下载使用
                    downloader.last_search_results = books
            
            elif cmd.lower().startswith('download '):
                arg = cmd[9:].strip()
                if not hasattr(downloader, 'last_search_results') or not downloader.last_search_results:
                    console.print("[yellow]请先搜索书籍[/yellow]")
                    continue
                
                books_to_download = []
                
                if arg.lower() == 'all':
                    books_to_download = downloader.last_search_results
                elif '-' in arg:
                    # 范围选择，如 1-5
                    try:
                        start, end = map(int, arg.split('-'))
                        books_to_download = downloader.last_search_results[start-1:end]
                    except:
                        console.print("[red]无效的范围格式[/red]")
                        continue
                elif ',' in arg:
                    # 多选，如 1,3,5
                    try:
                        indices = [int(x.strip()) for x in arg.split(',')]
                        books_to_download = [downloader.last_search_results[i-1] for i in indices]
                    except:
                        console.print("[red]无效的序号格式[/red]")
                        continue
                else:
                    # 单选
                    try:
                        index = int(arg)
                        books_to_download = [downloader.last_search_results[index-1]]
                    except:
                        console.print("[red]无效的序号[/red]")
                        continue
                
                if books_to_download:
                    downloader.batch_download(books_to_download)
            
            elif cmd.lower() == 'retry':
                if not hasattr(downloader, 'last_failed_books') or not downloader.last_failed_books:
                    console.print("[yellow]没有失败的下载需要重试[/yellow]")
                    continue
                
                failed_count = len(downloader.last_failed_books)
                console.print(f"[cyan]准备重试 {failed_count} 本失败的书籍...[/cyan]")
                downloader.batch_download(downloader.last_failed_books, is_retry=True)
            
            elif cmd.lower().startswith('file '):
                filepath = cmd[5:].strip()
                downloader.search_and_download_from_file(filepath)
            
            else:
                console.print("[yellow]未知命令，输入 help 查看帮助[/yellow]")
        
        except KeyboardInterrupt:
            console.print("\n[dim]使用 exit 退出程序[/dim]")
        except Exception as e:
            console.print(f"[red]错误: {e}[/red]")


def main():
    parser = argparse.ArgumentParser(description='Z-Library 批量下载工具')
    parser.add_argument('-s', '--search', help='搜索关键词')
    parser.add_argument('-f', '--file', help='从文件读取书名列表')
    parser.add_argument('-d', '--download', help='下载搜索结果 (all/序号)')
    parser.add_argument('-p', '--page', type=int, default=1, help='搜索页码')
    parser.add_argument('-i', '--interactive', action='store_true', help='交互模式')
    
    args = parser.parse_args()
    
    downloader = ZLibraryDownloader()
    
    # 检查登录状态
    if not downloader._check_login_status():
        console.print("[yellow]未登录，尝试自动登录...[/yellow]")
        if not downloader.login():
            console.print("[red]登录失败，部分功能可能受限[/red]")
    
    if args.interactive or (not args.search and not args.file):
        interactive_mode(downloader)
    elif args.file:
        downloader.search_and_download_from_file(args.file)
    elif args.search:
        books = downloader.search(args.search, page=args.page)
        downloader.display_books(books)
        
        if args.download and books:
            if args.download.lower() == 'all':
                downloader.batch_download(books)
            else:
                try:
                    indices = [int(x.strip()) for x in args.download.split(',')]
                    selected = [books[i-1] for i in indices]
                    downloader.batch_download(selected)
                except:
                    console.print("[red]无效的下载参数[/red]")


if __name__ == "__main__":
    main()

