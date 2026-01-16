#!/usr/bin/env python3
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

BASE = Path.home() / "dlbox"
DOWNLOAD_DIR = BASE / "downloads"
META_DIR = BASE / "meta"
LOGS_DIR = BASE / "logs"

ARIA2_SESSION = META_DIR / "session.txt"
ARIA2_LOG = LOGS_DIR / "aria2.log"


def ensure_dirs() -> None:
    for p in (DOWNLOAD_DIR, META_DIR, LOGS_DIR):
        p.mkdir(parents=True, exist_ok=True)
    ARIA2_SESSION.touch(exist_ok=True)


def run(cmd: list[str]) -> int:
    try:
        proc = subprocess.run(cmd, check=False)
        return proc.returncode
    except FileNotFoundError:
        print("Error: aria2c not found. Install aria2 first.", file=sys.stderr)
        return 127


def is_running() -> bool:
    # Works in most WSL distros.
    try:
        out = subprocess.check_output(
            ["bash", "-lc", "pgrep -x aria2c >/dev/null && echo yes || echo no"]
        )
        return out.decode().strip() == "yes"
    except Exception:
        return False


def start_daemon(connections: int, split: int, max_concurrent: int, seed_time: int) -> int:
    """
    Start aria2 in the background with a persistent session file.
    """
    ensure_dirs()

    if is_running():
        print("aria2 is already running.")
        return 0

    cmd = [
        "aria2c",
        "--enable-rpc=false",  # keep it simple (no JSON-RPC)
        f"--dir={str(DOWNLOAD_DIR)}",
        f"--input-file={str(ARIA2_SESSION)}",
        f"--save-session={str(ARIA2_SESSION)}",
        "--save-session-interval=10",
        f"--dht-file-path={str(META_DIR)}",
        f"--max-concurrent-downloads={max_concurrent}",
        f"--max-connection-per-server={connections}",
        f"--split={split}",
        "--continue=true",
        "--check-certificate=true",
        "--allow-overwrite=false",
        "--auto-file-renaming=true",
        "--summary-interval=5",
        "--log-level=notice",
        f"--log={str(ARIA2_LOG)}",
        "--daemon=true",
        f"--seed-time={seed_time}",  # 0 = don't seed (relevant for torrents)
    ]

    rc = run(cmd)
    if rc == 0:
        print(
            "Started aria2 background downloader.\n"
            f"Downloads: {DOWNLOAD_DIR}\n"
            f"Session:   {ARIA2_SESSION}\n"
            f"Log:       {ARIA2_LOG}"
        )
    return rc


def stop_daemon() -> int:
    if not is_running():
        print("aria2 is not running.")
        return 0
    rc = run(["bash", "-lc", "pkill -x aria2c"])
    if rc == 0:
        print("Stopped aria2.")
    return rc


def add_urls(urls: list[str]) -> int:
    ensure_dirs()

    # If running, kick off a one-off aria2c process to download immediately.
    # If not running, just queue into the session file for next start.
    if is_running():
        cmd = [
            "aria2c",
            "--continue=true",
            f"--dir={str(DOWNLOAD_DIR)}",
            f"--dht-file-path={str(META_DIR)}",
            "--check-certificate=true",
            "--allow-overwrite=false",
            "--auto-file-renaming=true",
            "--summary-interval=5",
            "--log-level=notice",
            f"--log={str(ARIA2_LOG)}",
            "--daemon=false",
        ] + urls
        return run(cmd)

    with ARIA2_SESSION.open("a", encoding="utf-8") as f:
        for u in urls:
            u = u.strip()
            if u:
                f.write(u + "\n")

    print(f"Queued {len(urls)} URL(s) into session file. Run: python3 ~/dlbox/dlbox.py start")
    return 0


def list_queue() -> int:
    ensure_dirs()
    lines = [ln.strip() for ln in ARIA2_SESSION.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        print("(queue empty)")
        return 0
    for i, u in enumerate(lines, 1):
        print(f"{i:>3}. {u}")
    return 0


def clear_queue() -> int:
    ensure_dirs()
    ARIA2_SESSION.write_text("", encoding="utf-8")
    print("Cleared session queue.")
    return 0


def resolve_file_arg(file_arg: str) -> Path:
    """
    If the user passes a bare filename, assume it lives in DOWNLOAD_DIR.
    Otherwise, respect the given path.
    """
    p = Path(file_arg).expanduser()
    if not p.is_absolute():
        candidate = DOWNLOAD_DIR / p
        if candidate.exists():
            return candidate
    return p


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):  # 1 MiB chunks
            h.update(chunk)
    return h.hexdigest()


def normalize_hex(s: str) -> str:
    return "".join(s.strip().lower().split())


def hinted_int(x: int) -> int:
    return max(1, int(x))


def main() -> int:
    p = argparse.ArgumentParser(
        prog="dlbox",
        description="Minimal $0 seedbox-like downloader (HTTPS) using aria2 + Python.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("start", help="Start aria2 in background (uses session queue).")
    s.add_argument("--connections", type=int, default=8, help="Max connections per server (default: 8).")
    s.add_argument("--split", type=int, default=8, help="Number of splits per download (default: 8).")
    s.add_argument("--max-concurrent", type=int, default=3, help="Max concurrent downloads (default: 3).")
    s.add_argument("--seed-time", type=int, default=0, help="Seed time for torrents in minutes (default: 0).")

    sub.add_parser("stop", help="Stop background aria2.")
    a = sub.add_parser("add", help="Add one or more URLs to download (or queue if aria2 not running).")
    a.add_argument("urls", nargs="+", help="HTTPS URL(s) to download.")
    sub.add_parser("queue", help="Show queued URLs in the session file.")
    sub.add_parser("clear", help="Clear queued URLs in the session file.")
    sub.add_parser("status", help="Show whether aria2 is running and where files go.")

    h = sub.add_parser("sha256", help="Print the SHA-256 of a file.")
    h.add_argument("file", help="Path to the file (relative or absolute).")

    v = sub.add_parser("verify", help="Verify a downloaded file against an expected SHA-256.")
    v.add_argument("file", help="Path to the downloaded file (relative or absolute).")
    v.add_argument("--sha256", required=True, help="Expected SHA-256 hex string.")

    args = p.parse_args()

    if args.cmd == "start":
        return start_daemon(args.connections, args.split, hinted_int(args.max_concurrent), args.seed_time)

    if args.cmd == "stop":
        return stop_daemon()

    if args.cmd == "add":
        return add_urls(args.urls)

    if args.cmd == "queue":
        return list_queue()

    if args.cmd == "clear":
        return clear_queue()

    if args.cmd == "status":
        ensure_dirs()
        print(f"Running:   {'yes' if is_running() else 'no'}")
        print(f"Downloads: {DOWNLOAD_DIR}")
        print(f"Session:   {ARIA2_SESSION}")
        print(f"Log:       {ARIA2_LOG}")
        return 0

    if args.cmd == "sha256":
        ensure_dirs()
        pth = resolve_file_arg(args.file)
        if not pth.exists():
            print(f"Error: file not found: {pth}", file=sys.stderr)
            return 2
        print(sha256_file(pth))
        return 0

    if args.cmd == "verify":
        ensure_dirs()
        pth = resolve_file_arg(args.file)
        if not pth.exists():
            print(f"Error: file not found: {pth}", file=sys.stderr)
            return 2

        expected = normalize_hex(args.sha256)
        actual = sha256_file(pth)

        if actual == expected:
            print("OK: SHA-256 matches.")
            return 0

        print("FAIL: SHA-256 does NOT match.")
        print(f"Expected: {expected}")
        print(f"Actual:   {actual}")
        return 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
