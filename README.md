# Understanding GitHub Copilot Suggestions – System Uptime Script

This repository contains `copilot_test.py`, a Python script that prints how long the system has been running (uptime). I started from code that **GitHub Copilot** generated on GitHub.com and then improved it to make it more secure and reliable.

---

## 1. How I used Copilot

1. Opened GitHub.com with GitHub Copilot enabled.
2. In my repository, clicked **Add file → Create new file** and named it `copilot_test.py`.
3. Committed the empty file to the `main` branch.
4. Opened Copilot Chat on the file and sent this prompt:
   > Create a script to print system uptime in copilot_test.py file

## 2. What Copilot generated

Copilot suggested a short script that runs the `uptime` command through `os.popen()`:

```python
import os

def get_uptime():
    uptime = os.popen('uptime -p').read()
    return uptime

print(get_uptime())
```

The suggestion met the basic requirement (it prints the uptime on Linux), so I accepted it as a starting point.

## 3. Did I modify it? Why?

Yes. The original version had several weaknesses:

| Problem in Copilot's code | Why it matters | What I changed |
|---|---|---|
| `os.popen()` runs the command through a **shell** | Shell execution can be a security risk (command injection) and gives no control over errors | Replaced with `subprocess.run()` using an argument list (no `shell=True`) |
| No error handling | If `uptime` is missing or fails, the script crashes or prints nothing | Added `try/except` for `FileNotFoundError`, `TimeoutExpired`, `CalledProcessError`, `OSError`, `ValueError` |
| No timeout | A hanging command would block the script forever | Added `timeout=5` |
| Exit code not checked | Failures went unnoticed | Added `check=True` and the script returns exit code `1` on error |
| `uptime -p` only works on Linux | The script failed on macOS and Windows | Linux reads `/proc/uptime` directly, Windows uses `GetTickCount64`, and macOS/BSD fall back to `uptime` |
| All code at top level | Hard to test and reuse | Split into functions (`format_seconds`, `uptime_from_proc`, `uptime_from_windows`, `uptime_from_command`, `get_uptime`, `main`) plus an `if __name__ == "__main__":` guard |

The output is also easier to read, for example `System uptime: 3 days, 4 hours, 12 minutes`.

## 4. How I tested it

- Ran the script on Linux and checked that the output matched the `uptime -p` command.
- Tested the formatting function on its own with known values:
  - `format_seconds(0)` → `0 seconds`
  - `format_seconds(3661)` → `1 hour, 1 minute`
  - `format_seconds(90061)` → `1 day, 1 hour, 1 minute`
- Checked that the script exits with code `0` on success (`echo $?`).
- Tested error handling by temporarily pointing the code at a file that doesn't exist. The script printed a clear error message and exited with code `1` instead of crashing.

## 5. How to run the script

**Requirements:** Python 3.7 or newer. No extra packages are needed.

```bash
# Clone the repository
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# Run the script
python3 copilot_test.py        # Linux / macOS
python copilot_test.py         # Windows
```

Example output:

```
System uptime: 2 days, 5 hours, 37 minutes
```

## 6. What I learned

- Copilot quickly produces working code, but it doesn't always follow best practices for security or portability.
- It's important to review AI-generated code instead of accepting it blindly, especially when it runs system commands.
- Copilot is a good starting point, and the developer is still responsible for making the code robust.
