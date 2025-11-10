import json
import os
from typing import Set

STATE_DIR = os.path.join("logs", "runs")


def ensure_dirs():
    os.makedirs("logs", exist_ok=True)
    os.makedirs(STATE_DIR, exist_ok=True)


def _state_path(change_id: str):
    return os.path.join(STATE_DIR, f"{change_id}.json")


def load_completed(change_id: str) -> Set[str]:
    path = _state_path(change_id)
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return set(data.get("completed", []))
        except json.JSONDecodeError:
            return set()


def mark_completed(change_id: str, ip: str):
    path = _state_path(change_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
    completed = set(data.get("completed", []))
    completed.add(ip)
    data["completed"] = sorted(completed)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
