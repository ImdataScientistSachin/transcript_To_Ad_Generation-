"""Simple RQ worker entrypoint.

Run this in a separate process to process queued storyboard render jobs.

Usage:
  python scripts/worker.py
"""
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from rq import Worker, Queue
except Exception as e:
    # Provide a clear error early if dependencies are missing; the message
    # helps developers install the required packages to run the worker.
    logger.error("Missing rq/redis dependencies: %s", e)
    raise


def main():
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    from redis import from_url
    try:
        conn = from_url(redis_url)
        # Create a queue bound to our connection and run a worker for it
        q = Queue("default", connection=conn)
        worker = Worker([q.name], connection=conn)
        logger.info("Starting RQ worker")
        worker.work()
    except Exception as e:
        # Provide actionable guidance when Redis isn't reachable. This is
        # commonly due to Docker not running or REDIS_URL being misconfigured.
        logger.error("Failed to connect to Redis at %s: %s", redis_url, e)
        logger.error(
            "Ensure Redis is running or set REDIS_URL to a reachable Redis"
            " instance before starting the worker."
        )
        raise


if __name__ == "__main__":
    main()
