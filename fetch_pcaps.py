#!/usr/bin/env python3
"""
Polls the competition platform for new pcaps and downloads them into ./pcaps/.
Files are prefixed with their source label to differentiate origins.

Run in a loop while the CTF is active:
    while true; do python3 fetch_pcaps.py; sleep 30; done
"""

import os
import sys
from pathlib import Path

import requests

# ── Add or remove endpoints here ─────────────────────────────────────────────
ENDPOINTS = [
    ("ad2", "https://platform.overseers.es3n1n.io/ad/2/pcap"),
    ("ad4", "https://platform.overseers.es3n1n.io/ad/4/pcap"),
    ("ad5", "https://platform.overseers.es3n1n.io/ad/5/pcap"),
]
# ─────────────────────────────────────────────────────────────────────────────

TIMEOUT = 5  # seconds for connectivity check and downloads

SCRIPT_DIR = Path(__file__).parent
DEST_DIR = SCRIPT_DIR / "pcaps"
DEST_DIR.mkdir(exist_ok=True)

# Load token from .env if not set in environment
token = os.environ.get("PLATFORM_TOKEN")
if not token:
    env_file = SCRIPT_DIR / ".env"
    for line in env_file.read_text().splitlines():
        if line.startswith("PLATFORM_TOKEN="):
            token = line.split("=", 1)[1].strip().strip("\"'")
            break

if not token or token == "CHANGE_ME":
    print("ERROR: Set PLATFORM_TOKEN in .env or export it before running.", file=sys.stderr)
    sys.exit(1)

headers = {"Authorization": f"Bearer {token}"}


def check_reachable(label: str, url: str) -> bool:
    try:
        r = requests.get(url, headers=headers, timeout=TIMEOUT)
        r.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"[{label}] Unreachable ({e}), skipping.")
        return False


def fetch_from(label: str, url: str) -> None:
    try:
        r = requests.get(url, headers=headers, timeout=TIMEOUT)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"[{label}] Failed to list pcaps: {e}")
        return

    data = r.json()
    names = data if isinstance(data, list) else data.get("pcaps", data.get("files", []))

    downloaded = 0
    for name in names:
        name = name.split("/")[-1]  # strip any path prefix
        local_file = DEST_DIR / f"{label}_{name}"
        if local_file.exists():
            continue
        print(f"[{label}] Downloading: {name}")
        try:
            resp = requests.get(f"{url}/{name}", headers=headers, timeout=60, stream=True)
            resp.raise_for_status()
            local_file.write_bytes(resp.content)
            downloaded += 1
        except requests.RequestException as e:
            print(f"[{label}] Failed to download {name}: {e}")
            local_file.unlink(missing_ok=True)

    print(f"[{label}] Done. Downloaded {downloaded} new pcap(s).")


reachable = [(label, url) for label, url in ENDPOINTS if check_reachable(label, url)]

if not reachable:
    print("No endpoints reachable, exiting.")
    sys.exit(0)

for label, url in reachable:
    fetch_from(label, url)
