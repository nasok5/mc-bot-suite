"""
Единая точка запуска: поднимает bot-core (Node.js) и UI (Python).

Использование:
    python run.py            # запустить всё вместе
    python run.py --separate # только UI (bot-core запусти отдельно)
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BOT_CORE = ROOT / "bot-core"
APP = ROOT / "app"


def start_node():
    """Запустить bot-core в отдельном процессе."""
    if not (BOT_CORE / "package.json").exists():
        print("[run] Не найден bot-core/package.json — пропускаю Node.")
        return None

    npm = "npm.cmd" if os.name == "nt" else "npm"
    print("[run] Запускаю bot-core...")
    proc = subprocess.Popen(
        [npm, "start"],
        cwd=str(BOT_CORE),
        shell=(os.name == "nt"),
    )
    # Дать время подняться WS-серверу
    time.sleep(2)
    return proc


def start_ui():
    """Запустить Python UI."""
    print("[run] Запускаю UI...")
    python = sys.executable
    return subprocess.Popen([python, "main.py"], cwd=str(APP))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--separate",
        action="store_true",
        help="Не запускать bot-core, только UI (запустите Node вручную)",
    )
    args = parser.parse_args()

    node_proc = None
    if not args.separate:
        node_proc = start_node()

    ui_proc = start_ui()

    try:
        ui_proc.wait()
    except KeyboardInterrupt:
        pass
    finally:
        if ui_proc and ui_proc.poll() is None:
            ui_proc.terminate()
        if node_proc and node_proc.poll() is None:
            node_proc.terminate()
            try:
                node_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                node_proc.kill()


if __name__ == "__main__":
    main()