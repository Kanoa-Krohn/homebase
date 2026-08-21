import subprocess
import re
import os
import shutil
import socket
import time


def _get_wifi_info():
    signal = None
    ssid = None
    try:
        out = subprocess.run(['iwconfig'], capture_output=True, text=True, timeout=2).stdout
        match_quality = re.search(r'Link Quality=(\d+)/(\d+)', out)
        if match_quality:
            signal = round(int(match_quality.group(1)) / int(match_quality.group(2)) * 100)
        match_ssid = re.search(r'ESSID:"([^"]*)"', out)
        if match_ssid:
            ssid = match_ssid.group(1)
    except Exception:
        pass
    return signal, ssid


def _get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def _get_cpu_temp():
    try:
        out = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True, timeout=2).stdout
        match = re.search(r'temp=([\d.]+)', out)
        if match:
            return round(float(match.group(1)))
    except Exception:
        pass
    return None


def _get_cpu_usage():
    try:
        load1, _, _ = os.getloadavg()
        cpu_count = os.cpu_count() or 1
        return min(100, round((load1 / cpu_count) * 100))
    except Exception:
        return None


def _get_mem_used_pct():
    try:
        with open('/proc/meminfo') as f:
            meminfo = f.read()
        total = int(re.search(r'MemTotal:\s+(\d+)', meminfo).group(1))
        available = int(re.search(r'MemAvailable:\s+(\d+)', meminfo).group(1))
        return round((1 - available / total) * 100)
    except Exception:
        return None


def _get_disk_used_pct():
    try:
        total, used, free = shutil.disk_usage('/')
        return round((used / total) * 100)
    except Exception:
        return None


def _get_uptime():
    try:
        with open('/proc/uptime') as f:
            uptime_seconds = float(f.read().split()[0])
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        if days > 0:
            return f"{days}d {hours}h"
        minutes = int((uptime_seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
    except Exception:
        return None


def get_system_stats():
    wifi_signal, wifi_ssid = _get_wifi_info()
    return {
        'wifi_signal': wifi_signal,
        'wifi_ssid': wifi_ssid,
        'ip_address': _get_ip_address(),
        'uptime': _get_uptime(),
        'cpu_temp': _get_cpu_temp(),
        'cpu_usage': _get_cpu_usage(),
        'mem_used_pct': _get_mem_used_pct(),
        'disk_used_pct': _get_disk_used_pct(),
    }


def check_internet_connected():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.5)
        s.connect(('8.8.8.8', 80))
        s.close()
        return True
    except Exception:
        return False


def reconnect_wifi():
    try:
        subprocess.run(['sudo', 'nmcli', 'radio', 'wifi', 'off'], timeout=10)
        time.sleep(2)
        subprocess.run(['sudo', 'nmcli', 'radio', 'wifi', 'on'], timeout=10)
        time.sleep(3)
        subprocess.run(['sudo', 'nmcli', 'device', 'connect', 'wlan0'], capture_output=True, text=True, timeout=20)

        for _ in range(5):
            time.sleep(2)
            if check_internet_connected():
                return True
        return False
    except Exception:
        return False