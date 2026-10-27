from pathlib import Path
import subprocess
import sys
import os

root = Path(__file__).resolve().parents[1]
cwd = root / "crwaler" / "pcparts"
logs = root / ".tmp" / "crawl_20261027"
logs.mkdir(parents=True, exist_ok=True)
categories = sys.argv[1:] or ["cpu", "gpu", "mainboard", "ram", "ssd", "psu"]
env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
for category in categories:
    if category not in {"cpu", "gpu", "mainboard", "ram", "ssd", "psu"}:
        raise ValueError(category)
    print(f"START {category}", flush=True)
    with (logs / f"{category}.log").open("w", encoding="utf-8") as log:
        proc = subprocess.Popen(
            [sys.executable, "-u", f"{category}_playwright.py"],
            cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
        )
        for line in proc.stdout:
            log.write(line)
            log.flush()
            print(line, end="", flush=True)
        code = proc.wait()
    print(f"END {category}: exit={code}", flush=True)
    if code:
        sys.exit(code)
