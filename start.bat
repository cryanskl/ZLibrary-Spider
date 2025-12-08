@echo off
REM Z-Library 下载器启动脚本 (Windows)

REM 设置代码页为 UTF-8
chcp 65001 >nul 2>&1

REM 获取脚本所在目录
cd /d "%~dp0"

echo Z-Library 下载器启动脚本
echo ================================

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.7 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查 Python 版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [✓] Python 版本: %PYTHON_VERSION%

REM 检查虚拟环境
if not exist "venv" (
    echo [提示] 未找到虚拟环境，正在创建...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo [✓] 虚拟环境创建成功
)

REM 激活虚拟环境
echo [提示] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查并安装依赖
if not exist "venv\.deps_installed" (
    echo [提示] 正在安装依赖包...
    python -m pip install --upgrade pip -q
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
    echo. > venv\.deps_installed
    echo [✓] 依赖安装完成
) else (
    echo [✓] 依赖已安装
)

REM 检查配置文件
if not exist ".env" (
    echo [提示] 未找到 .env 文件，请配置账号信息
    echo 创建 .env 文件并添加以下内容：
    echo ZLIB_EMAIL=your_email@example.com
    echo ZLIB_PASSWORD=your_password
    echo.
)

echo.
echo [提示] 启动程序...
echo ================================
echo.

REM 运行程序（默认交互模式）
python zlib_downloader.py %*

REM 如果直接双击运行，保持窗口打开
if "%1"=="" pause

