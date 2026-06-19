#!/bin/bash
# OpenCore Ultra v5.0 一键安装脚本

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║   █████╗ ██╗    ██████╗  ██████╗ ██╗  ██╗  v5.0 ULTIMATE      ║"
echo "║  ██╔══██╗██║    ██╔══██╗██╔═══██╗╚██╗██╔╝  MIT License        ║"
echo "║  ███████║██║    ██████╔╝██║   ██║ ╚███╔╝   50+ Models         ║"
echo "║  ██╔══██║██║    ██╔══██╗██║   ██║ ██╔██╗   30+ Roles          ║"
echo "║  ██║  ██║██║    ██████╔╝╚██████╔╝██╔╝ ██╗   Full Animation    ║"
echo "║  ╚═╝  ╚═╝╚═╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝   Inspired by Qiyu  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[✗] Python3 未安装，请先安装 Python3"
    exit 1
fi

echo "[✓] Python3 已安装: $(python3 --version)"

# 安装依赖
echo "[*] 正在安装依赖..."
pip3 install -r requirements.txt

# 创建工具目录
mkdir -p tools

# 设置执行权限
chmod +x opencore_tool.py

echo ""
echo "[✓] 安装完成！"
echo ""
echo "使用方法:"
echo "  命令行模式: python3 opencore_tool.py"
echo "  图形界面:   python3 opencore_tool.py --gui"
echo ""
echo "打包 EXE:    python3 build_exe.py"
