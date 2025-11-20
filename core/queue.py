"""Queue helpers using RQ (Redis Queue).

This module provides a simple enqueue helper that will schedule a
storyboard rendering job in Redis. The worker (see `scripts/worker.py`)
should be run separately to process jobs.

If Redis isn't available the app should fall back to the local thread
renderer (handled by `app.py`).
"""
import os
import typing
import logging
from typing import Any

from .video import render_storyboard_preview

logger = logging.getLogger(__name__)

# Pre-declare variables with Any so mypy won't complain when we assign None
redis: Any = None
Queue: Any = None
get_current_job: Any = None
Job: Any = None
try:
    import redis
    from rq import Queue, get_current_job
    from rq.job import Job
except Exception:
    redis = None
    Queue = None
    get_current_job = None
    Job = None


# NOTE: The queue helpers are intentionally small: they wrap `rq`'s API
# to enqueue the CPU/IO-heavy `render_storyboard_preview` function so a
# separate worker process can perform rendering without blocking the
# Streamlit web UI. The web UI handles the fallback to a local thread
# renderer when Redis/RQ aren't available.


def _get_redis_conn():
    url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    if redis is None:
        raise RuntimeError("redis package not installed")
    return redis.from_url(url)


def enqueue_render(frames: typing.List[str], images: typing.List[str], options: dict) -> str:
    """Enqueue a render job, return job id.

    Raises RuntimeError if Redis isn't available.
    """
    if Queue is None:
        # Important: the web UI falls back to a thread-based renderer when
        # RQ/Redis is not available. Calling code can catch this and use the
        # local fallback to keep the dev experience smooth.
        raise RuntimeError("rq/redis not available")
    conn = _get_redis_conn()
    q = Queue(connection=conn)
    job = q.enqueue(_render_job, frames, images or [], options)
    return job.id


def get_job_status(job_id: str) -> dict:
    if Job is None:
        return {"status": "unavailable"}
    try:
        conn = _get_redis_conn()
        job = Job.fetch(job_id, connection=conn)
        meta = job.meta or {}
        return {"status": job.get_status(), "meta": meta, "result": job.result}
    except Exception as e:
        # Failures here are typically transient (Redis restart) or due to
        # job reaping; surface a readable error to the caller so the UI can
        # display helpful messaging.
        logger.exception("Failed to fetch job status for %s", job_id)
        return {"status": "error", "error": str(e)}


def _render_job(frames, images, options):
    """Internal worker function executed by RQ.

    This updates job.meta with progress values and returns the output
    file path when complete.
    """
    job = None
    if get_current_job is not None:
        try:
            job = get_current_job()
        except Exception:
            job = None

    def _cb(p: int, status: str = ""):
        if job is not None:
            job.meta["progress"] = int(p)
            job.meta["status"] = status
            job.save_meta()

    # Delegate to the MoviePy-based renderer. We pass a small callback that
    # updates the RQ job metadata so callers can poll progress via `get_job_status`.
    out = render_storyboard_preview(
        frames,
        images=images,
        resolution=options.get("resolution", (720, 1280)),
        fps=options.get("fps", 24),
        crossfade=options.get("crossfade", 0.5),
        progress_callback=_cb,
    )
    if job is not None:
        job.meta["progress"] = 100
        job.meta["status"] = out
        job.save_meta()
    return out
