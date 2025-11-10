import json
import os
import time
from typing import Dict, Any

LOG_DIR = os.path.join("logs")


def _now_iso():
    return time.strftime("%Y-%m-%dT%H-%M-%S")


def make_log_path(change_id: str):
    ts = _now_iso()
    filename = f"{ts}__{change_id}.json"
    return os.path.join(LOG_DIR, filename)


class JsonLogger:
    """
    Simple append-only JSONL logger: one JSON object per line.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # create file if not exists
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write("")

    def write(self, record: Dict[str, Any]):
        record = dict(record)
        record["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
