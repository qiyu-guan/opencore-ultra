# core/system.py - 系统修改与优化
from .utils import run_cmd
from config import ADB_EXE

def edit_build_prop(dev: str, key: str, value: str) -> bool:
    # 需要 root
    cmd = f"{ADB_EXE} -s {dev} shell su -c \"sed -i 's/^{key}=.*/{key}={value}/' /system/build.prop\""
    _, _, code = run_cmd(cmd)
    return code == 0

def set_dpi(dev: str, dpi: int) -> bool:
    cmd = f"{ADB_EXE} -s {dev} shell wm density {dpi}"
    _, _, code = run_cmd(cmd)
    return code == 0

def set_resolution(dev: str, width: int, height: int) -> bool:
    cmd = f"{ADB_EXE} -s {dev} shell wm size {width}x{height}"
    _, _, code = run_cmd(cmd)
    return code == 0

def update_hosts(dev: str, hosts_file: str) -> bool:
    # 推送 hosts 文件到 /system/etc/hosts (需root)
    cmd = f"{ADB_EXE} -s {dev} push {hosts_file} /system/etc/hosts"
    _, _, code = run_cmd(cmd)
    return code == 0
