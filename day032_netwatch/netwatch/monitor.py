from __future__ import annotations
import re
import subprocess
import platform
from typing import Optional


def ping_host(address: str, count: int = 3) -> tuple[bool, Optional[float]]:
    """ping を実行し (success, avg_rtt_ms) を返す。"""
    system = platform.system()
    if system == "Windows":
        cmd = ["ping", "-n", str(count), address]
    else:
        cmd = ["ping", "-c", str(count), "-W", "2", address]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10 + count * 2,
        )
    except subprocess.TimeoutExpired:
        return False, None

    if result.returncode != 0:
        return False, None

    rtt_ms = _parse_avg_rtt(result.stdout, system)
    return True, rtt_ms


def _parse_avg_rtt(output: str, system: str) -> Optional[float]:
    if system == "Windows":
        m = re.search(r"平均\s*=\s*([\d.]+)\s*ms|Average\s*=\s*([\d.]+)\s*ms", output)
    else:
        # macOS: round-trip min/avg/max/stddev = 1.234/2.345/3.456/0.123 ms
        # Linux: rtt min/avg/max/mdev = 1.234/2.345/3.456/0.123 ms
        m = re.search(r"(?:round-trip|rtt)[^=]+=\s*[\d.]+/([\d.]+)/", output)
    if not m:
        return None
    val = next(v for v in m.groups() if v is not None)
    return float(val)


def traceroute_host(address: str, max_hops: int = 30) -> list[dict]:
    """traceroute を実行してホップ一覧を返す。"""
    system = platform.system()
    if system == "Windows":
        cmd = ["tracert", "-h", str(max_hops), address]
    else:
        cmd = ["traceroute", "-m", str(max_hops), "-w", "2", address]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []

    return _parse_traceroute(result.stdout, system)


def _parse_traceroute(output: str, system: str) -> list[dict]:
    hops: list[dict] = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue

        # ホップ番号を先頭から取得
        hop_match = re.match(r"^\s*(\d+)\s+", line)
        if not hop_match:
            continue
        hop_num = int(hop_match.group(1))

        # * * * は到達不能ホップ
        if re.search(r"\*\s+\*\s+\*", line):
            hops.append({"hop_num": hop_num, "address": None, "rtt_ms": None})
            continue

        # IP アドレスまたはホスト名
        addr_match = re.search(
            r"(\d{1,3}(?:\.\d{1,3}){3}|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", line
        )
        address = addr_match.group(1) if addr_match else None

        # RTT (最初の数値 ms)
        rtt_match = re.search(r"([\d.]+)\s*ms", line)
        rtt_ms = float(rtt_match.group(1)) if rtt_match else None

        hops.append({"hop_num": hop_num, "address": address, "rtt_ms": rtt_ms})
    return hops
