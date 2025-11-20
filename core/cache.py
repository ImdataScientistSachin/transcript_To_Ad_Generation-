"""Simple file-backed cache for small payloads.

Provides `get_cached` and `set_cached` functions. Cache entries are stored
under `.cache/` as JSON files named by SHA256(key). TTL support is
available via `expires_at` timestamp in the stored object.
"""
from typing import Any, Optional
import os
import json
import hashlib
import time


CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", ".cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _key_to_path(key: str) -> str:
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{h}.json")


def get_cached(key: str) -> Optional[Any]:
    path = _key_to_path(key)
    try:
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        expires_at = payload.get("expires_at")
        if expires_at and time.time() > expires_at:
            try:
                os.remove(path)
            except Exception:
                # If deletion fails, log and continue; stale entry will be ignored
                try:
                    import logging

                    logging.getLogger(__name__).exception("Failed to remove expired cache file %s", path)
                except Exception:
                    pass
            return None
        return payload.get("value")
    except Exception:
        try:
            import logging

            logging.getLogger(__name__).exception("Failed to read cache file %s", path)
        except Exception:
            pass
        return None


def set_cached(key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
    path = _key_to_path(key)
    payload = {"value": value}
    if ttl_seconds is not None:
        payload["expires_at"] = time.time() + ttl_seconds
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    os.replace(tmp, path)


def purge_cache(older_than_seconds: int = 60 * 60 * 24 * 7) -> int:
    """Remove cache files older than `older_than_seconds`.

    Returns the number of files removed.
    """
    removed = 0
    try:
        now = time.time()
        for fname in os.listdir(CACHE_DIR):
            path = os.path.join(CACHE_DIR, fname)
            try:
                mtime = os.path.getmtime(path)
                if now - mtime > older_than_seconds:
                    os.remove(path)
                    removed += 1
            except Exception:
                try:
                    import logging

                    logging.getLogger(__name__).exception("Failed to inspect/remove cache file %s", path)
                except Exception:
                    pass
                continue
    except Exception:
        try:
            import logging

            logging.getLogger(__name__).exception("Failed to purge cache directory %s", CACHE_DIR)
        except Exception:
            pass
    return removed


def get_last_cleanup() -> float:
    """Return the timestamp (epoch) of the last cleanup, or 0 if none."""
    p = os.path.join(CACHE_DIR, "last_cleanup.json")
    try:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                d = json.load(f)
            return float(d.get("last", 0))
    except Exception:
        pass
    return 0.0


def set_last_cleanup(ts: float) -> None:
    p = os.path.join(CACHE_DIR, "last_cleanup.json")
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"last": ts}, f)
    except Exception:
        pass
