# core/backup.py - 备份功能
from .utils import run_cmd
from config import ADB_EXE
import time, gzip, tarfile
from pathlib import Path

def full_flash_backup(dev: str, out_dir: Path, compress=True) -> bool:
    # find mmcblk0 / sda
    cmd = f"{ADB_EXE} -s {dev} shell \"ls /dev/block/ | grep -E '^mmcblk[0-9]+$|^sda$'\""
    out, _, _ = run_cmd(cmd)
    targets = out.splitlines()
    target = None
    for t in targets:
        if t in ('mmcblk0', 'sda'):
            target = t; break
    if not target and targets:
        target = targets[0]
    if not target:
        return False
    name = f"full_flash_{time.strftime('%Y%m%d_%H%M%S')}.img"
    if compress:
        name += ".gz"
    local = out_dir / name
    remote = f"/sdcard/{name}"
    if compress:
        cmd = f"{ADB_EXE} -s {dev} shell su -c \"dd if=/dev/block/{target} bs=4M 2>/dev/null | gzip > {remote}\""
    else:
        cmd = f"{ADB_EXE} -s {dev} shell su -c \"dd if=/dev/block/{target} bs=4M of={remote}\""
    _, _, code = run_cmd(cmd, timeout=3600)
    if code != 0 and "records" not in out:
        return False
    pull = f"{ADB_EXE} -s {dev} pull {remote} \"{local}\""
    _, _, code2 = run_cmd(pull, timeout=3600)
    run_cmd(f"{ADB_EXE} -s {dev} shell rm {remote}")
    return code2 == 0

def backup_partition(dev: str, part: str, out_dir: Path) -> bool:
    paths = [
        f"/dev/block/by-name/{part}",
        f"/dev/block/by-slot/{part}",
        f"/dev/block/by-label/{part}",
        f"/dev/block/{part}"
    ]
    for p in paths:
        test = f"{ADB_EXE} -s {dev} shell su -c \"test -e {p} && echo ok\""
        out, _, _ = run_cmd(test)
        if "ok" in out:
            local = out_dir / f"{part}.img"
            remote = f"/sdcard/{part}.img"
            cmd = f"{ADB_EXE} -s {dev} shell su -c \"dd if={p} of={remote} bs=4M\""
            _, _, code = run_cmd(cmd, timeout=120)
            if code == 0:
                run_cmd(f"{ADB_EXE} -s {dev} pull {remote} \"{local}\"")
                run_cmd(f"{ADB_EXE} -s {dev} shell rm {remote}")
                return True
    return False

def backup_apps(dev: str, out_dir: Path) -> bool:
    out, _, _ = run_cmd(f"{ADB_EXE} -s {dev} shell pm list packages -3")
    pkgs = [l.split(':')[-1] for l in out.splitlines() if l]
    for pkg in pkgs:
        out2, _, _ = run_cmd(f"{ADB_EXE} -s {dev} shell pm path {pkg}")
        apk_path = out2.split(':')[-1].strip()
        if apk_path:
            run_cmd(f"{ADB_EXE} -s {dev} pull {apk_path} \"{out_dir}/{pkg}.apk\"")
    return True

def backup_contacts(dev: str, out_file: str) -> bool:
    cmd = f"{ADB_EXE} -s {dev} shell content query --uri content://contacts/phones"
    out, _, code = run_cmd(cmd)
    if code == 0:
        with open(out_file, 'w') as f:
            f.write(out)
        return True
    return False
# 其他备份（短信、WiFi等）可类似实现
