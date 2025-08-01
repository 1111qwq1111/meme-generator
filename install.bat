@echo off
chcp 65001 >nul
echo ========================================
echo    Meme Generator 一键安装脚本 (Windows)
echo ========================================
echo.

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到Python，请先安装Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [SUCCESS] Python环境检查通过

echo.
echo [2/4] 进入core目录并安装依赖...
cd core
if not exist requirements.txt (
    echo [ERROR] 未找到requirements.txt文件
    pause
    exit /b 1
)

echo 正在安装Python依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] 依赖安装失败，请检查网络连接或Python环境
    pause
    exit /b 1
)
echo [SUCCESS] 依赖安装完成

echo.
echo [3/4] 设置额外meme仓库...
python setup_meme_repos.py
if errorlevel 1 (
    echo [WARNING] 额外meme仓库设置失败，将使用内置meme
)

echo.
echo [4/4] 启动meme-generator服务...
echo 服务将在 http://localhost:2233 启动
echo 按 Ctrl+C 可停止服务
echo.
echo ========================================
echo    安装完成！正在启动服务...
echo ========================================
echo.

python -m meme_generator.app

echo.
echo 服务已停止
pause