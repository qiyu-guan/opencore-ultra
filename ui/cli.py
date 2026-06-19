# ui/cli.py - 命令行菜单
import sys, time, os
from pathlib import Path
from core import device, backup, flash, firmware, root, system, rescue
from config import LOG_FILE, TOOL_DIR, ADB_EXE, FASTBOOT_EXE, EDL_EXE
import threading

GREEN = '\033[32m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_green(text):
    print(f"{GREEN}{text}{RESET}")

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print_green(r"""
╔══════════════════════════════════════════════════════════════════╗
║   █████╗ ██╗    ██████╗  ██████╗ ██╗  ██╗  v5.0 ULTIMATE      ║
║  ██╔══██╗██║    ██╔══██╗██╔═══██╗╚██╗██╔╝  MIT License        ║
║  ███████║██║    ██████╔╝██║   ██║ ╚███╔╝   50+ Models         ║
║  ██╔══██║██║    ██╔══██╗██║   ██║ ██╔██╗   30+ Roles          ║
║  ██║  ██║██║    ██████╔╝╚██████╔╝██╔╝ ██╗   Full Animation    ║
║  ╚═╝  ╚═╝╚═╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝   Inspired by Qiyu  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

def run_cli():
    print_banner()
    while True:
        print_green("\n主菜单:")
        print_green("  1. 检测设备")
        print_green("  2. 备份分区")
        print_green("  3. 字库备份/恢复")
        print_green("  4. 刷机 (Fastboot)")
        print_green("  5. 救砖模式 (EDL)")
        print_green("  6. 固件管理")
        print_green("  7. Root/系统修改")
        print_green("  8. 安全擦除")
        print_green("  9. 切换至图形界面 (GUI)")
        print_green("  0. 退出")
        choice = input("请选择: ").strip()

        if choice == '1':
            mode, dev, info = device.detect_device()
            if mode:
                print_green(f"模式: {mode}, 设备: {dev}")
                print_green(f"详细信息: {info}")
            else:
                print_green("未检测到设备")
        elif choice == '2':
            mode, dev, _ = device.detect_device()
            if mode != 'adb':
                print_green("仅ADB模式支持备份")
                continue
            parts = device.get_partitions(mode, dev)
            if not parts:
                print_green("无法获取分区列表，请输入分区名（逗号分隔）")
                sel = input("> ")
                parts = [p.strip() for p in sel.split(',') if p.strip()]
            else:
                for i,p in enumerate(parts):
                    print_green(f"{i+1}. {p}")
                idx = input("输入编号(逗号分隔): ")
                parts = [parts[int(i)-1] for i in idx.split(',') if i.isdigit()]
            out_dir = Path(f"./backup_{time.strftime('%Y%m%d_%H%M%S')}")
            out_dir.mkdir()
            for p in parts:
                if backup.backup_partition(dev, p, out_dir):
                    print_green(f"备份 {p} 成功")
                else:
                    print_green(f"备份 {p} 失败")
        elif choice == '3':
            mode, dev, _ = device.detect_device()
            if mode != 'adb':
                print_green("仅ADB模式支持字库备份")
                continue
            out_dir = Path("./full_backup")
            out_dir.mkdir(exist_ok=True)
            if backup.full_flash_backup(dev, out_dir):
                print_green("字库备份成功")
            else:
                print_green("字库备份失败")
        elif choice == '4':
            mode, dev, _ = device.detect_device()
            if mode != 'fastboot':
                print_green("请先进入fastboot模式")
                continue
            img = input("输入镜像路径: ")
            part = input("输入分区名: ")
            if flash.fastboot_flash(dev, part, img):
                print_green("刷入成功")
            else:
                print_green("刷入失败")
        elif choice == '5':
            rescue.rescue_menu()  # 内嵌菜单
        elif choice == '6':
            print_green("固件管理功能 (待完善)")
        elif choice == '7':
            print_green("Root/系统修改功能 (待完善)")
        elif choice == '8':
            print_green("安全擦除功能 (待完善)")
        elif choice == '9':
            print_green("启动图形界面...")
            from ui.gui import run_gui
            run_gui()
            return
        elif choice == '0':
            print_green("退出程序")
            sys.exit(0)
        else:
            print_green("无效选项")
        input("\n按Enter继续...")
        print_banner()
