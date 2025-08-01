#!/bin/bash

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================"
echo -e "   Meme Generator 一键安装脚本 (Linux/macOS)"
echo -e "========================================${NC}"
echo

echo -e "${BLUE}[1/4] 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}[ERROR] 未找到Python，请先安装Python 3.9+${NC}"
        echo "Ubuntu/Debian: sudo apt-get install python3 python3-pip"
        echo "CentOS/RHEL: sudo yum install python3 python3-pip"
        echo "macOS: brew install python3"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# 检查Python版本
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}[SUCCESS] 找到Python版本: $PYTHON_VERSION${NC}"

echo
echo -e "${BLUE}[2/4] 进入core目录并安装依赖...${NC}"
cd core

if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}[ERROR] 未找到requirements.txt文件${NC}"
    exit 1
fi

echo "正在安装Python依赖包..."
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo -e "${RED}[ERROR] 未找到pip，请先安装pip${NC}"
    exit 1
fi

$PIP_CMD install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] 依赖安装失败，请检查网络连接或Python环境${NC}"
    exit 1
fi
echo -e "${GREEN}[SUCCESS] 依赖安装完成${NC}"

echo
echo -e "${BLUE}[3/4] 设置额外meme仓库...${NC}"
$PYTHON_CMD setup_meme_repos.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING] 额外meme仓库设置失败，将使用内置meme${NC}"
fi

echo
echo -e "${BLUE}[4/4] 启动meme-generator服务...${NC}"
echo "服务将在 http://localhost:2233 启动"
echo "按 Ctrl+C 可停止服务"
echo
echo -e "${GREEN}========================================"
echo -e "    安装完成！正在启动服务..."
echo -e "========================================${NC}"
echo

# 捕获Ctrl+C信号
trap 'echo -e "\n${YELLOW}服务已停止${NC}"; exit 0' INT

$PYTHON_CMD -m meme_generator.app