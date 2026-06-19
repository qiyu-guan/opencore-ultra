# core/device.py - 设备检测与管理
from .utils import run_cmd
from config import ADB_EXE, FASTBOOT_EXE, EDL_EXE
import re
from typing import Optional, Tuple, List, Dict

def detect_device() -> Tuple[Optional[str], Optional[str], Dict]:
    info = {}
    # ADB
    out, _, _ = run_cmd(f"{ADB_EXE} devices")
    for line in out.splitlines():
        if line and "device" in line and not "List" in line:
            dev = line.split()[0]
            info['adb_device'] = dev
            # get model
            p, _, _ = run_cmd(f"{ADB_EXE} -s {dev} shell getprop ro.product.model")
            info['model'] = p.strip()
            return "adb", dev, info
    # Fastboot
    out, _, _ = run_cmd(f"{FASTBOOT_EXE} devices")
    for line in out.splitlines():
        if line and "fastboot" in line:
            dev = line.split()[0]
            info['fastboot_device'] = dev
            return "fastboot", dev, info
    # EDL
    if EDL_EXE.exists():
        out, _, _ = run_cmd(f"{EDL_EXE} info")
        if "Qualcomm" in out:
            info['edl_device'] = "EDL-Device"
            return "edl", "EDL-Device", info
    return None, None, info

def get_partitions(mode: str, dev: str) -> List[str]:
    if mode != "adb":
        return []
    paths = [
        "/dev/block/by-name/",
        "/dev/block/by-slot/",
        "/dev/block/by-label/",
        "/dev/block/"
    ]
    for base in paths:
        cmd = f"{ADB_EXE} -s {dev} shell \"ls {base} 2>/dev/null\""
        out, _, _ = run_cmd(cmd)
        if out and "No such file" not in out:
            parts = [p.strip() for p in out.splitlines() if p.strip() and re.match(r'^[a-zA-Z]', p.strip())]
            if parts:
                return parts
    return []

def get_device_info(mode: str, dev: str) -> Dict:
    info = {}
    if mode == "adb":
        out, _, _ = run_cmd(f"{ADB_EXE} -s {dev} shell getprop")
        for line in out.splitlines():
            if "ro.boot.flash.locked" in line:
                info['locked'] = line.split(':')[-1].strip().strip('[]')
        return info
    if mode == "fastboot":
        out, _, _ = run_cmd(f"{FASTBOOT_EXE} -s {dev} getvar all")
        info['fastboot_vars'] = out
        return info
    return info
