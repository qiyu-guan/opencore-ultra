# config.py - 全局配置
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
TOOL_DIR = BASE_DIR / "tools"
ADB_EXE = TOOL_DIR / "adb.exe"
FASTBOOT_EXE = TOOL_DIR / "fastboot.exe"
EDL_EXE = TOOL_DIR / "edl.exe"

PLATFORM_TOOLS_URL = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
EDL_URL = "https://github.com/bkerler/edl/releases/latest/download/edl.exe"

TIMEOUT_FLASH = 300
TIMEOUT_BACKUP = 120
TIMEOUT_DOWNLOAD = 600
DOWNLOAD_RETRIES = 3

BACKUP_COMPRESS = True
BACKUP_ENCRYPT = False
LOG_FILE = BASE_DIR / "opencore_ultra.log"

GUI_TITLE = "OpenCore Ultra v5.0"
GUI_GEOMETRY = "1000x700"
