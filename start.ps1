# Z-Library 下载器启动脚本 (Windows PowerShell)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "Z-Library 下载器启动脚本" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# 检查 Python 是否安装
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[✓] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[错误] 未找到 Python，请先安装 Python 3.7 或更高版本" -ForegroundColor Red
    Write-Host "下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "按 Enter 键退出"
    exit 1
}

# 检查虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "[提示] 未找到虚拟环境，正在创建..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 创建虚拟环境失败" -ForegroundColor Red
        Read-Host "按 Enter 键退出"
        exit 1
    }
    Write-Host "[✓] 虚拟环境创建成功" -ForegroundColor Green
}

# 激活虚拟环境
Write-Host "[提示] 激活虚拟环境..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# 检查并安装依赖
if (-not (Test-Path "venv\.deps_installed")) {
    Write-Host "[提示] 正在安装依赖包..." -ForegroundColor Yellow
    python -m pip install --upgrade pip -q
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 依赖安装失败" -ForegroundColor Red
        Read-Host "按 Enter 键退出"
        exit 1
    }
    New-Item -Path "venv\.deps_installed" -ItemType File -Force | Out-Null
    Write-Host "[✓] 依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "[✓] 依赖已安装" -ForegroundColor Green
}

# 检查配置文件
if (-not (Test-Path ".env")) {
    Write-Host "[提示] 未找到 .env 文件，请配置账号信息" -ForegroundColor Yellow
    Write-Host "创建 .env 文件并添加以下内容："
    Write-Host "ZLIB_EMAIL=your_email@example.com"
    Write-Host "ZLIB_PASSWORD=your_password"
    Write-Host ""
}

Write-Host ""
Write-Host "[提示] 启动程序..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# 运行程序（默认交互模式）
python zlib_downloader.py $args

# 如果直接运行，保持窗口打开
if ($args.Count -eq 0) {
    Read-Host "按 Enter 键退出"
}

