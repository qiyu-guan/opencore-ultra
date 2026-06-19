# core/utils.py - 通用工具
import subprocess
import time
import logging
import hashlib
import requests
from pathlib import Path
from typing import Tuple

def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def run_cmd(cmd: str, timeout: int = 60) -> Tuple[str, str, int]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout", -1
    except Exception as e:
        return "", str(e), -1

def download_file(url: str, dest: Path, resume=True, retries=3) -> bool:
    for attempt in range(retries):
        try:
            headers = {'Range': f'bytes={dest.stat().st_size}-'} if resume and dest.exists() else {}
            r = requests.get(url, stream=True, headers=headers, timeout=30)
            r.raise_for_status()
            mode = 'ab' if resume and dest.exists() else 'wb'
            with open(dest, mode) as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk: f.write(chunk)
            return True
        except Exception as e:
            time.sleep(2)
    return False

def md5sum(path: Path) -> str:
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256sum(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()
