#!/usr/bin/env python3
"""
copilot_test.py - Print the system uptime.

Original GitHub Copilot suggestion (kept here for reference):

    import os

    def get_uptime():
        uptime = os.popen('uptime -p').read()
        return uptime

    print(get_uptime())

Improvements made:
  * Replaced os.popen() with subprocess.run() (no shell, argument list,
    timeout, return-code checking).
  * Split the logic into small functions with exception handling.
  * Read /proc/uptime directly on Linux (no external process needed).
  * Added fallbacks for macOS/BSD (`uptime` command) and Windows
    (GetTickCount64 via ctypes).
  * Human-readable output and a non-zero exit code on failure.
"""

import platform
import subprocess
import sys


def format_seconds(total_seconds: float) -> str:
    """Convert a number of seconds into 'X days, Y hours, Z minutes'."""
    total_seconds = int(total_seconds)
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    return ", ".join(parts)


def uptime_from_proc() -> float:
    """Linux: read uptime in seconds from /proc/uptime."""
    try:
        with open("/proc/uptime", "r", encoding="utf-8") as f:
            return float(f.readline().split()[0])
    except (OSError, ValueError, IndexError) as exc:
        raise RuntimeError(f"Could not read /proc/uptime: {exc}") from exc


def uptime_from_windows() -> float:
    """Windows: milliseconds since boot via GetTickCount64."""
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.GetTickCount64.restype = ctypes.c_ulonglong
        return kernel32.GetTickCount64() / 1000.0
    except (AttributeError, OSError) as exc:
        raise RuntimeError(f"Could not query Windows uptime: {exc}") from exc


def uptime_from_command() -> str:
    """macOS/BSD/other Unix: run the `uptime` command safely."""
    try:
        result = subprocess.run(
            ["uptime"],          # argument list, no shell=True
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        return result.stdout.strip()
    except FileNotFoundError as exc:
        raise RuntimeError("The 'uptime' command is not available.") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("The 'uptime' command timed out.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"'uptime' failed with exit code {exc.returncode}: {exc.stderr.strip()}"
        ) from exc


def get_uptime() -> str:
    """Return a human-readable uptime string for the current OS."""
    system = platform.system()

    if system == "Linux":
        return format_seconds(uptime_from_proc())
    if system == "Windows":
        return format_seconds(uptime_from_windows())
    # macOS, BSD, etc.
    return uptime_from_command()


def main() -> int:
    try:
        print(f"System uptime: {get_uptime()}")
        return 0
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
