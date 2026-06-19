# core/flash.py - 刷写引擎
from .utils import run_cmd
from config import ADB_EXE, FASTBOOT_EXE, EDL_EXE
import time, zipfile, tempfile, shutil
from pathlib import Path

def reboot_bootloader(dev: str) -> bool:
    run_cmd(f"{ADB_EXE} -s {dev} reboot bootloader")
    time.sleep(5)
    return True

def fastboot_flash(dev: str, part: str, image: str) -> bool:
    cmd = f"{FASTBOOT_EXE} -s {dev} flash {part} \"{image}\""
    _, _, code = run_cmd(cmd, timeout=300)
    return code == 0

def edl_flash(part: str, image: str) -> bool:
    if not EDL_EXE.exists(): return False
    cmd = f"{EDL_EXE} w {part} \"{image}\""
    _, _, code = run_cmd(cmd, timeout=300)
    return code == 0

def fastboot_flash_all(zip_path: str, dev: str) -> bool:
    with zipfile.ZipFile(zip_path, 'r') as zf:
        with tempfile.TemporaryDirectory() as tmpdir:
            zf.extractall(tmpdir)
            imgs = list(Path(tmpdir).glob("*.img"))
            for img in imgs:
                part = img.stem
                if not fastboot_flash(dev, part, str(img)):
                    return False
    return True

def flash_custom_recovery(dev: str, recovery_img: str) -> bool:
    return fastboot_flash(dev, "recovery", recovery_img)

def fastboot_wipe(dev: str) -> bool:
    cmd = f"{FASTBOOT_EXE} -s {dev} -w"
    _, _, code = run_cmd(cmd)
    return code == 0
