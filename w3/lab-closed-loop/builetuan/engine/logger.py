"""Structured JSON logger for the closed-loop orchestrator.

Every log record is emitted as a single JSON line to stdout, making it easy
to parse by Loki/Promtail and other log aggregation pipelines.

Required fields per the lab spec: ts, event_type, service, action, result.
Additional context is merged via **kwargs.
"""

import json
import os
from datetime import datetime, timezone


# Optional: write audit log to a JSONL file for Loki/Promtail ingestion
_AUDIT_LOG_PATH = os.environ.get("AUDIT_LOG_PATH", "audit_log.jsonl")


class JsonLogger:
    """Emit structured JSON log records to stdout + optional audit file."""

    def __init__(self, name: str):
        self._name = name

    def _emit(self, level: str, event_type: str, **kwargs):
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "logger": self._name,
            "level": level,
            "event_type": event_type,
            **kwargs,
        }
        line = json.dumps(record)
        print(line, flush=True)

        # Append to audit log file for Grafana/Loki dashboard
        try:
            with open(_AUDIT_LOG_PATH, "a") as f:
                f.write(line + "\n")
        except OSError:
            pass  # non-critical — do not crash on audit write failure

    def info(self, event_type: str, **kwargs):
        self._emit("INFO", event_type, **kwargs)

    def warning(self, event_type: str, **kwargs):
        self._emit("WARNING", event_type, **kwargs)

    def error(self, event_type: str, **kwargs):
        self._emit("ERROR", event_type, **kwargs)
