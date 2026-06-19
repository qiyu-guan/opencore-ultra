# core/root.py - Root 与模块管理（完整版）
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from .utils import run_cmd
from config import ADB_EXE


# ============ 1. Magisk Boot 修补 ============
def patch_boot_for_magisk(dev: str, boot_img: Path, 
                          magisk_apk: Path = None) -> Optional[Path]:
    """
    使用 Magisk 修补 boot.img
    需要手机已安装 Magisk
    返回: 修补后的boot路径，失败返回None
    """
    if not boot_img.exists():
        return None
    
    # 推送boot到手机
    remote_boot = "/sdcard/boot_to_patch.img"
    run_cmd(f"{ADB_EXE} -s {dev} push \"{boot_img}\" {remote_boot}")
    
    # 使用Magisk修补 (通过am broadcast)
    cmd = f"{ADB_EXE} -s {dev} shell \"am broadcast -a com.topjohnwu.magisk.PATCH_BOOT -e path {remote_boot}\""
    out, err, code = run_cmd(cmd)
    
    # 检查修补结果
    check_cmd = f"{ADB_EXE} -s {dev} shell ls /sdcard/magisk_patched*.img 2>/dev/null"
    out2, _, _ = run_cmd(check_cmd)
    
    if out2:
        patched_remote = out2.split()[0]
        patched_local = boot_img.parent / f"magisk_patched_{boot_img.name}"
        pull_cmd = f"{ADB_EXE} -s {dev} pull {patched_remote} \"{patched_local}\""
        run_cmd(pull_cmd)
        run_cmd(f"{ADB_EXE} -s {dev} shell rm {patched_remote}")
        run_cmd(f"{ADB_EXE} -s {dev} shell rm {remote_boot}")
        return patched_local
    
    return None


# ============ 2. Magisk 模块管理 ============
def install_magisk_module(dev: str, module_zip: Path) -> bool:
    """安装 Magisk 模块"""
    if not module_zip.exists():
        return False
    
    remote_zip = "/sdcard/magisk_module.zip"
    run_cmd(f"{ADB_EXE} -s {dev} push \"{module_zip}\" {remote_zip}")
    
    # 使用 Magisk 安装
    cmd = f"{ADB_EXE} -s {dev} shell su -c \"magisk --install-module {remote_zip}\""
    out, err, code = run_cmd(cmd, timeout=60)
    
    run_cmd(f"{ADB_EXE} -s {dev} shell rm {remote_zip}")
    return code == 0 or "Done" in out


def list_magisk_modules(dev: str) -> List[Dict]:
    """列出已安装的Magisk模块"""
    cmd = f"{ADB_EXE} -s {dev} shell su -c \"magisk --list-modules\""
    out, _, code = run_cmd(cmd)
    modules = []
    if code == 0:
        for line in out.splitlines():
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    modules.append({
                        'id': parts[0],
                        'name': ' '.join(parts[1:]),
                        'enabled': True
                    })
    return modules


def remove_magisk_module(dev: str, module_id: str) -> bool:
    """移除Magisk模块"""
    cmd = f"{ADB_EXE} -s {dev} shell su -c \"magisk --remove-module {module_id}\""
    _, _, code = run_cmd(cmd)
    return code == 0


# ============ 3. 在线模块浏览 ============
def get_online_modules() -> List[Dict]:
    """
    从 Magisk 官方仓库获取在线模块列表
    实际需要解析 GitHub repo，这里返回示例
    """
    try:
        import requests
        # 使用 Magisk-Modules-Repo API
        url = "https://magisk-modules-repo-api.pages.dev/modules.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [{
                'id': m.get('id', ''),
                'name': m.get('name', ''),
                'version': m.get('version', ''),
                'download': m.get('download', ''),
                'description': m.get('description', ''),
                'author': m.get('author', ''),
            } for m in data.get('modules', [])]
    except:
        pass
    return []


def download_online_module(module_id: str, dest_dir: Path) -> Optional[Path]:
    """下载在线模块"""
    import requests
    url = f"https://github.com/Magisk-Modules-Repo/{module_id}/releases/latest"
    # 获取实际下载链接（简化）
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # 从页面提取zip链接（简化）
            import re
            match = re.search(r'href="([^"]+\.zip)"', response.text)
            if match:
                zip_url = match.group(1)
                if not zip_url.startswith('http'):
                    zip_url = 'https://github.com' + zip_url
                dest = dest_dir / f"{module_id}.zip"
                from .utils import download_file
                if download_file(zip_url, dest):
                    return dest
    except:
        pass
    return None


# ============ 4. 挂载系统为可读写 ============
def mount_system_rw(dev: str, partition: str = "/") -> bool:
    """挂载系统分区为可读写"""
    # 尝试多种方法
    methods = [
        f"mount -o rw,remount {partition}",
        f"mount -o rw,remount /dev/block/by-name/system {partition}",
        f"mount -o rw,remount /dev/block/bootdevice/by-name/system {partition}"
    ]
    for method in methods:
        cmd = f"{ADB_EXE} -s {dev} shell su -c \"{method}\""
        _, _, code = run_cmd(cmd)
        if code == 0:
            return True
    return False


# ============ 5. 应用管理 ============
def uninstall_package(dev: str, pkg: str, keep_data: bool = False) -> bool:
    """卸载应用（系统或用户）"""
    cmd = f"{ADB_EXE} -s {dev} shell pm uninstall {'-k' if keep_data else ''} {pkg}"
    _, _, code = run_cmd(cmd)
    return code == 0


def disable_package(dev: str, pkg: str) -> bool:
    """禁用应用（冻结）"""
    cmd = f"{ADB_EXE} -s {dev} shell pm disable {pkg}"
    _, _, code = run_cmd(cmd)
    return code == 0


def enable_package(dev: str, pkg: str) -> bool:
    """启用应用"""
    cmd = f"{ADB_EXE} -s {dev} shell pm enable {pkg}"
    _, _, code = run_cmd(cmd)
    return code == 0


def list_packages(dev: str, filter_str: str = None) -> List[Dict]:
    """列出已安装应用"""
    cmd = f"{ADB_EXE} -s {dev} shell pm list packages -f"
    if filter_str:
        cmd += f" | grep {filter_str}"
    out, _, code = run_cmd(cmd)
    pkgs = []
    if code == 0:
        for line in out.splitlines():
            if line:
                parts = line.split('=')
                if len(parts) == 2:
                    pkgs.append({
                        'path': parts[0].replace('package:', ''),
                        'name': parts[1],
                        'is_system': '/system/' in parts[0]
                    })
    return pkgs


# ============ 6. SELinux 管理 ============
def set_selinux_mode(dev: str, mode: str) -> bool:
    """切换 SELinux 模式 permissive/enforcing"""
    if mode not in ('permissive', 'enforcing'):
        return False
    val = '0' if mode == 'permissive' else '1'
    cmd = f"{ADB_EXE} -s {dev} shell su -c \"setenforce {val}\""
    _, _, code = run_cmd(cmd)
    if code == 0:
        return True
    # 备用方法
    alt_cmd = f"{ADB_EXE} -s {dev} shell \"setenforce {val}\""
    _, _, code = run_cmd(alt_cmd)
    return code == 0


def get_selinux_status(dev: str) -> str:
    """获取SELinux状态"""
    cmd = f"{ADB_EXE} -s {dev} shell getenforce"
    out, _, code = run_cmd(cmd)
    if code == 0:
        return out.strip().lower()
    return 'unknown'


# ============ 7. LSPosed 管理 ============
def install_lsposed(dev: str, module_zip: Path) -> bool:
    """安装 LSPosed 模块"""
    # 类似 Magisk 模块安装
    return install_magisk_module(dev, module_zip)


def lsposed_modules(dev: str) -> List[Dict]:
    """列出 LSPosed 模块"""
    cmd = f"{ADB_EXE} -s {dev} shell ls /data/adb/lspd/modules/"
    out, _, code = run_cmd(cmd)
    if code == 0:
        return [{'id': m, 'enabled': True} for m in out.splitlines() if m]
    return []


# ============ 8. 内核调校 ============
def set_cpu_governor(dev: str, governor: str) -> bool:
    """设置CPU调度器"""
    # 需root且内核支持
    cmd = f"{ADB_EXE} -s {dev} shell su -c \"echo {governor} > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor\""
    _, _, code = run_cmd(cmd)
    return code == 0


def get_cpu_governor(dev: str) -> str:
    """获取当前CPU调度器"""
    cmd = f"{ADB_EXE} -s {dev} shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null"
    out, _, code = run_cmd(cmd)
    if code == 0:
        return out.strip()
    return 'unknown'
