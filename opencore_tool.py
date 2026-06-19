#!/usr/bin/env python3
# opencore_tool.py - 程序入口
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="OpenCore Ultra v5.0")
    parser.add_argument('--gui', action='store_true', help='启动图形界面')
    parser.add_argument('--cli', action='store_true', help='强制命令行模式')
    args = parser.parse_args()

    if args.gui:
        from ui.gui import run_gui
        run_gui()
    else:
        from ui.cli import run_cli
        run_cli()

if __name__ == '__main__':
    main()
