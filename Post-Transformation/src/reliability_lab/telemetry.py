import json
import logging
import time
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger("agent_reliability")

def configure_logging():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

def emit(event: str, **fields: Any):
    payload = {"event": event, "ts": time.time(), **fields}
    logger.info(json.dumps(payload, default=str))

@contextmanager
def span(event: str, **fields: Any):
    start = time.perf_counter()
    emit(event + ".start", **fields)
    try:
        yield
        emit(event + ".success",
             latency_ms=round((time.perf_counter()-start)*1000, 2), **fields)
    except Exception as exc:
        emit(event + ".failure",
             latency_ms=round((time.perf_counter()-start)*1000, 2),
             error=type(exc).__name__, message=str(exc), **fields)
        raise
