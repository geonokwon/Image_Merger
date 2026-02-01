#!/bin/bash
# Image Merger 실행 (Mac). 더블클릭하거나 터미널에서 실행하세요.
# Cursor/IDE 백그라운드에서 실행하면 부모 프로세스가 먼저 종료되어 크래시할 수 있음.

cd "$(dirname "$0")"

if [[ -d ".venv" ]]; then
    .venv/bin/python main.py
elif [[ -d "/tmp/imgtest_venv" ]]; then
    /tmp/imgtest_venv/bin/python main.py
else
    echo "가상환경이 없습니다. 먼저 실행: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    python3 -m venv .venv 2>/dev/null && .venv/bin/pip install -q -r requirements.txt && .venv/bin/python main.py
fi
