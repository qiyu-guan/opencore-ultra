# core/firmware.py - 固件管理（完整版）
import os
import json
import re
import zipfile
import tempfile
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from .utils import download_file, md5sum, sha256sum, run_cmd
from config import TOOL_DIR

# 固件源配置（可扩展）
FIRMWARE_SOURCES = {
    "xiaomi": {
        "url": "https://xiaomifirmwareupdater.com/api/v1/",
        "type": "xiaomi"
    },
    "google": {
        "url": "https://developers.google.com/android/ota",
        "type": "google"
    },
    "oneplus": {
        "url": "https://oxygenos.oneplus.net/",
        "type": "oneplus"
    }
}

# 缓存目录
CACHE_DIR = TOOL_DIR / "firmware_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ============ 1. 设备型号识别 ============
def identify_device_model(adb_dev: str = None) -> Dict[str, str]:
    """
    识别设备型号信息
    返回: { 'device': 'cancro', 'brand': 'Xiaomi', 'model': 'MI 3' }
    """
    info = {}
    if adb_dev:
        cmds = [
            f"adb -s {adb_dev} shell getprop ro.product.device",
            f"adb -s {adb_dev} shell getprop ro.product.brand",
            f"adb -s {adb_dev} shell getprop ro.product.model",
            f"adb -s {adb_dev} shell getprop ro.build.version.release",
            f"adb -s {adb_dev} shell getprop ro.build.version.sdk",
        ]
        keys = ['device', 'brand', 'model', 'android_version', 'sdk_version']
        for cmd, key in zip(cmds, keys):
            out, _, _ = run_cmd(cmd)
            info[key] = out.strip()
    else:
        # 尝试从 fastboot 获取
        out, _, _ = run_cmd("fastboot getvar product 2>/dev/null")
        if out and 'product' in out:
            info['device'] = out.split(':')[-1].strip()
    return info


# ============ 2. 固件匹配（真实可用的小米固件API） ============
def match_firmware(device: str, source: str = "xiaomi", 
                   branch: str = "stable") -> List[Dict]:
    """
    匹配固件（支持小米/Google/一加）
    返回: [ { 'name': '...', 'url': '...', 'version': '...', 'md5': '...' } ]
    """
    if source == "xiaomi":
        return _match_xiaomi_firmware(device, branch)
    elif source == "google":
        return _match_google_firmware(device)
    elif source == "oneplus":
        return _match_oneplus_firmware(device)
    return []


def _match_xiaomi_firmware(device: str, branch: str = "stable") -> List[Dict]:
    """从小米固件更新器 API 获取"""
    url = f"https://xiaomifirmwareupdater.com/api/v1/device/{device}/{branch}/"
    try:
        import requests
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            result = []
            for item in data.get('files', []):
                result.append({
                    'name': item.get('filename', ''),
                    'url': item.get('download', ''),
                    'version': item.get('version', ''),
                    'md5': item.get('md5', ''),
                    'size': item.get('size', 0),
                    'date': item.get('date', ''),
                    'type': item.get('type', ''),
                })
            return result
        else:
            # 备用: 尝试旧版API
            url2 = f"https://xiaomifirmwareupdater.com/api/vanilla/{device}/"
            response2 = requests.get(url2, timeout=30)
            if response2.status_code == 200:
                data2 = response2.json()
                result = []
                for item in data2.get('files', []):
                    result.append({
                        'name': item.get('filename', ''),
                        'url': item.get('download', ''),
                        'version': item.get('version', ''),
                        'md5': item.get('md5', ''),
                        'size': item.get('size', 0),
                        'date': item.get('date', ''),
                        'type': item.get('type', ''),
                    })
                return result
    except Exception as e:
        print(f"[!] 固件匹配失败: {e}")
    return []


def _match_google_firmware(device: str) -> List[Dict]:
    """Google 官方固件（Pixel系列）"""
    # 实际需要解析 https://developers.google.com/android/ota
    # 这里返回示例
    return [
        {"name": f"{device}-ota-latest.zip", 
         "url": f"https://dl.google.com/dl/android/aosp/{device}-ota-latest.zip",
         "version": "latest", "md5": ""}
    ]


def _match_oneplus_firmware(device: str) -> List[Dict]:
    """一加固件"""
    # 一加官方下载站
    return [
        {"name": f"{device}_13.0.0_OTA.zip",
         "url": f"https://oxygenos.oneplus.net/{device}_13.0.0_OTA.zip",
         "version": "13.0.0", "md5": ""}
    ]


# ============ 3. 固件下载 ============
def download_firmware(url: str, dest: Path, resume: bool = True) -> bool:
    """下载固件，支持断点续传"""
    return download_file(url, dest, resume=resume, retries=5)


def download_firmware_multi(urls: List[str], dest_dir: Path) -> List[Path]:
    """多线程下载多个固件"""
    import concurrent.futures
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}
        for url in urls:
            name = url.split('/')[-1] or 'firmware.zip'
            dest = dest_dir / name
            futures[executor.submit(download_file, url, dest)] = dest
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                results.append(futures[future])
    return results


# ============ 4. 固件校验 ============
def verify_firmware(file_path: Path, expected_md5: str = None, 
                    expected_sha256: str = None) -> Tuple[bool, Dict]:
    """
    校验固件完整性
    返回: (是否通过, { 'md5': '...', 'sha256': '...', 'size': ... })
    """
    result = {
        'md5': md5sum(file_path),
        'sha256': sha256sum(file_path),
        'size': file_path.stat().st_size,
        'valid': True
    }
    
    if expected_md5 and result['md5'] != expected_md5:
        result['valid'] = False
        result['error'] = f"MD5不匹配: 期望 {expected_md5}, 实际 {result['md5']}"
    elif expected_sha256 and result['sha256'] != expected_sha256:
        result['valid'] = False
        result['error'] = f"SHA256不匹配: 期望 {expected_sha256}, 实际 {result['sha256']}"
    
    # 检查是否为有效的ZIP
    if result['valid'] and zipfile.is_zipfile(file_path):
        result['is_zip'] = True
    else:
        result['is_zip'] = False
    
    return result['valid'], result


# ============ 5. Payload.bin 解包 ============
def extract_payload_bin(ota_zip: Path, out_dir: Path, 
                        partition: str = None) -> Dict[str, Path]:
    """
    解包 payload.bin（OTA增量包/完整包）
    返回: { 'boot': Path, 'system': Path, ... }
    """
    result = {}
    temp_dir = out_dir / "payload_extract"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(ota_zip, 'r') as zf:
        if 'payload.bin' not in zf.namelist():
            return {}
        zf.extract('payload.bin', temp_dir)
    
    payload_file = temp_dir / "payload.bin"
    
    # 使用 payload_dumper (需要安装: pip install payload-dumper)
    try:
        import payload_dumper
        # 调用payload_dumper
        dumper = payload_dumper.PayloadDumper(str(payload_file))
        images = dumper.parse()
        for img_name, img_data in images.items():
            if partition and img_name != partition:
                continue
            img_path = out_dir / f"{img_name}.img"
            with open(img_path, 'wb') as f:
                f.write(img_data)
            result[img_name] = img_path
    except ImportError:
        # 如果 payload-dumper 未安装，尝试使用外部工具
        if shutil.which('payload-dumper'):
            cmd = f"payload-dumper -o {out_dir} {payload_file}"
            run_cmd(cmd)
            for img in out_dir.glob("*.img"):
                result[img.stem] = img
        else:
            # 检查是否安装了 python-payload-dumper
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "payload-dumper"])
                # 重试
                from payload_dumper import PayloadDumper
                dumper = PayloadDumper(str(payload_file))
                images = dumper.parse()
                for img_name, img_data in images.items():
                    img_path = out_dir / f"{img_name}.img"
                    with open(img_path, 'wb') as f:
                        f.write(img_data)
                    result[img_name] = img_path
            except:
                print("[!] 请安装 payload-dumper: pip install payload-dumper")
    
    # 清理临时文件
    payload_file.unlink(missing_ok=True)
    temp_dir.rmdir()
    
    return result


# ============ 6. 固件版本对比 ============
def compare_firmware_versions(current: str, target: str) -> Dict:
    """
    对比固件版本，智能推荐升级/降级
    返回: { 'action': 'upgrade'/'downgrade'/'same', 'reason': '...' }
    """
    def parse_version(v):
        parts = re.findall(r'\d+', v)
        return tuple(int(p) for p in parts[:4])
    
    cur_parts = parse_version(current)
    tgt_parts = parse_version(target)
    
    if cur_parts == tgt_parts:
        return {'action': 'same', 'reason': '版本相同'}
    elif cur_parts < tgt_parts:
        # 检查是否可降级（防回滚保护）
        if int(cur_parts[0]) < int(tgt_parts[0]) - 1:
            return {'action': 'downgrade', 'reason': '跨大版本降级，可能有ARB风险'}
        return {'action': 'upgrade', 'reason': '新版本可用'}
    else:
        # 当前版本更高
        if int(cur_parts[0]) > int(tgt_parts[0]) + 1:
            return {'action': 'downgrade', 'reason': '跨大版本升级，可能有ARB风险'}
        return {'action': 'downgrade', 'reason': '可降级到目标版本'}


# ============ 7. 本地固件库管理 ============
class FirmwareLibrary:
    """本地固件库管理器"""
    
    def __init__(self, library_dir: Path = None):
        self.library_dir = library_dir or CACHE_DIR / "library"
        self.library_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.library_dir / "index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except:
                return {"firmwares": []}
        return {"firmwares": []}
    
    def _save_index(self):
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def add_firmware(self, file_path: Path, metadata: Dict = None):
        """添加固件到本地库"""
        if not file_path.exists():
            return False
        entry = {
            'path': str(file_path),
            'name': file_path.name,
            'size': file_path.stat().st_size,
            'md5': md5sum(file_path),
            'sha256': sha256sum(file_path),
            'metadata': metadata or {}
        }
        # 检查是否已存在
        for i, f in enumerate(self.index['firmwares']):
            if f['md5'] == entry['md5']:
                self.index['firmwares'][i] = entry
                self._save_index()
                return True
        self.index['firmwares'].append(entry)
        self._save_index()
        return True
    
    def search(self, keyword: str) -> List[Dict]:
        """搜索固件"""
        results = []
        keyword = keyword.lower()
        for f in self.index['firmwares']:
            if keyword in f['name'].lower():
                results.append(f)
        return results
    
    def get_by_device(self, device: str) -> List[Dict]:
        """按设备筛选"""
        results = []
        for f in self.index['firmwares']:
            meta = f.get('metadata', {})
            if meta.get('device') == device:
                results.append(f)
        return results
    
    def remove_firmware(self, md5: str) -> bool:
        """从本地库移除固件"""
        for i, f in enumerate(self.index['firmwares']):
            if f['md5'] == md5:
                # 删除文件
                path = Path(f['path'])
                if path.exists():
                    path.unlink()
                self.index['firmwares'].pop(i)
                self._save_index()
                return True
        return False
    
    def import_file(self, file_path: Path, device: str = None) -> bool:
        """导入拖拽的固件文件"""
        if not file_path.exists():
            return False
        # 尝试自动识别设备
        if not device:
            # 从文件名猜测
            patterns = [
                r'([a-z0-9_]+)_(global|cn|eu|in|ru)_',
                r'([a-z0-9_]+)-ota-',
                r'([a-z0-9_]+)\.',
            ]
            for p in patterns:
                match = re.search(p, file_path.name)
                if match:
                    device = match.group(1)
                    break
        metadata = {'device': device} if device else {}
        return self.add_firmware(file_path, metadata)


# ============ 8. 固件信息分析 ============
def analyze_firmware(file_path: Path) -> Dict:
    """
    分析固件文件信息
    返回: { 'type': 'ota'/'fastboot'/'recovery', 'partitions': [...], 'version': '...' }
    """
    result = {
        'type': 'unknown',
        'partitions': [],
        'version': '',
        'size': file_path.stat().st_size,
        'name': file_path.name,
        'is_zip': zipfile.is_zipfile(file_path),
    }
    
    if not file_path.exists():
        return result
    
    # 判断类型
    if file_path.suffix == '.img':
        result['type'] = 'image'
        result['partitions'] = [file_path.stem]
        return result
    
    if zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path, 'r') as zf:
            files = zf.namelist()
            # 检查 payload.bin
            if 'payload.bin' in files:
                result['type'] = 'ota'
            # 检查 fastboot 镜像
            img_files = [f for f in files if f.endswith('.img')]
            if img_files:
                result['partitions'] = [Path(f).stem for f in img_files]
                if not result['type']:
                    result['type'] = 'fastboot_package'
            # 检查 flash-all 脚本
            if any('flash-all' in f for f in files):
                result['type'] = 'fastboot_package'
            # 检查 recovery
            if 'recovery.img' in files:
                result['type'] = 'recovery_package'
    
    return result


# ============ 9. 固件版本对比 + 推荐 ============
def get_firmware_recommendation(device: str, current_version: str = None) -> Dict:
    """
    获取固件推荐
    """
    result = {
        'current_device': device,
        'current_version': current_version,
        'available': [],
        'recommendation': None,
    }
    
    # 获取可用固件
    fw_list = match_firmware(device)
    if not fw_list:
        return result
    
    result['available'] = fw_list
    
    # 如果有当前版本，进行对比
    if current_version:
        for fw in fw_list:
            version = fw.get('version', '')
            if version:
                compare = compare_firmware_versions(current_version, version)
                if compare['action'] in ('upgrade', 'downgrade'):
                    result['recommendation'] = {
                        'target': fw,
                        'action': compare['action'],
                        'reason': compare['reason']
                    }
                    break
    
    # 如果无版本信息，推荐最新
    if not result['recommendation'] and fw_list:
        # 按版本号排序
        try:
            sorted_fw = sorted(fw_list, 
                key=lambda x: tuple(int(p) for p in re.findall(r'\d+', x.get('version', '0.0.0'))), 
                reverse=True)
            result['recommendation'] = {
                'target': sorted_fw[0] if sorted_fw else None,
                'action': 'latest',
                'reason': '最新固件'
            }
        except:
            pass
    
    return result


# ============ 10. 固件下载进度回调 ============
def download_firmware_with_progress(url: str, dest: Path, 
                                    progress_callback=None) -> bool:
    """
    下载固件并报告进度
    progress_callback(percent, speed, eta)
    """
    import time
    try:
        import requests
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        total = int(response.headers.get('content-length', 0))
        downloaded = 0
        start_time = time.time()
        
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0 and progress_callback:
                        percent = (downloaded / total) * 100
                        elapsed = time.time() - start_time
                        speed = downloaded / elapsed if elapsed > 0 else 0
                        eta = (total - downloaded) / speed if speed > 0 else 0
                        progress_callback(percent, speed, eta)
        return True
    except Exception as e:
        print(f"[!] 下载失败: {e}")
        return False


# ============ 11. 固件解包验证 ============
def extract_firmware(firmware_path: Path, output_dir: Path) -> Dict:
    """
    解包固件（自动识别类型）
    返回: { 'type': '...', 'files': { 'partition': Path, ... } }
    """
    result = {
        'type': 'unknown',
        'files': {},
        'metadata': {}
    }
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not firmware_path.exists():
        return result
    
    # OTA包 (payload.bin)
    if zipfile.is_zipfile(firmware_path):
        with zipfile.ZipFile(firmware_path, 'r') as zf:
            if 'payload.bin' in zf.namelist():
                result['type'] = 'ota'
                result['files'] = extract_payload_bin(firmware_path, output_dir)
                return result
            
            # 普通zip（可能是fastboot包）
            zf.extractall(output_dir)
            img_files = list(output_dir.glob("*.img"))
            if img_files:
                result['type'] = 'fastboot_package'
                for img in img_files:
                    result['files'][img.stem] = img
                result['metadata']['flash_all'] = any(
                    output_dir.glob("*flash-all*")
                )
    else:
        # 单个镜像
        result['type'] = 'image'
        result['files'][firmware_path.stem] = firmware_path
    
    return result
