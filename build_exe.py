import PyInstaller.__main__
import sys
import os

if __name__ == '__main__':
    PyInstaller.__main__.run([
        'opencore_tool.py',
        '--onefile',
        '--windowed',  # 无控制台窗口（若需要GUI）
        '--name=OpenCore_Ultra_v5.0',
        '--add-data=core;core',
        '--add-data=ui;ui',
        '--hidden-import=tkinter',
        '--hidden-import=requests',
    ])
