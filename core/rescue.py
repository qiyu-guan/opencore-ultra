# core/rescue.py - 救砖与安全擦除
from .utils import run_cmd
from config import ADB_EXE, FASTBOOT_EXE, EDL_EXE

def edl_enter(dev: str) -> bool:
    # 通过adb进入edl
    run_cmd(f"{ADB_EXE} -s {dev} reboot edl")
    return True

def edl_info() -> str:
    out, _, _ = run_cmd(f"{EDL_EXE} info")
    return out

def edl_flash_all(zip_path: str) -> bool:
    # 使用edl刷写整个zip
    import zipfile, tempfile, shutil
    with zipfile.ZipFile(zip_path, 'r') as zf:
        with tempfile.TemporaryDirectory() as tmp:
            zf.extractall(tmp)
            imgs = list(Path(tmp).glob("*.img"))
            for img in imgs:
                part = img.stem
                if not edl_flash(part, str(img)):
                    return False
    return True

def frp_reset(dev: str) -> bool:
    # 需要特定命令，不同设备不同
    # 这里使用adb shell settings delete global frp
    cmd = f"{ADB_EXE} -s {dev} shell settings delete global frp"
    _, _, code = run_cmd(cmd)
    return code == 0

def secure_erase(dev: str, partition: str) -> bool:
    # 使用dd写零
    cmd = f"{ADB_EXE} -s {dev} shell su -c \"dd if=/dev/zero of=/dev/block/by-name/{partition}\""
    _, _, code = run_cmd(cmd)
    return code == 0
