#!/bin/bash
# Z-Library 下载器启动脚本 (Linux/macOS)

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Z-Library 下载器启动脚本${NC}"
echo "================================"

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python3，请先安装 Python 3.7 或更高版本${NC}"
    exit 1
fi

# 检查 Python 版本
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.7"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}错误: Python 版本过低，需要 Python 3.7 或更高版本，当前版本: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 版本: $PYTHON_VERSION${NC}"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}未找到虚拟环境，正在创建...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}创建虚拟环境失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
fi

# 激活虚拟环境
echo -e "${YELLOW}激活虚拟环境...${NC}"
source venv/bin/activate

# 检查并安装依赖
if [ ! -f "venv/.deps_installed" ]; then
    echo -e "${YELLOW}正在安装依赖包...${NC}"
    pip install --upgrade pip -q
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        touch venv/.deps_installed
        echo -e "${GREEN}✓ 依赖安装完成${NC}"
    else
        echo -e "${RED}依赖安装失败${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ 依赖已安装${NC}"
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}提示: 未找到 .env 文件，请配置账号信息${NC}"
    echo "创建 .env 文件并添加以下内容："
    echo "ZLIB_EMAIL=your_email@example.com"
    echo "ZLIB_PASSWORD=your_password"
fi

echo ""
echo -e "${GREEN}启动程序...${NC}"
echo "================================"
echo ""

# 运行程序（默认交互模式）
python3 zlib_downloader.py "$@"

