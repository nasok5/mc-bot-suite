#!/usr/bin/env bash
set -e
chmod +x run.sh
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] Python 3 не найден."
    exit 1
fi

if ! command -v node >/dev/null 2>&1; then
    echo "[ERROR] Node.js не найден."
    exit 1
fi

python3 run.py
