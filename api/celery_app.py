import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Celery instance used by the API just to send messages
celery_client = Celery(
    "nexusparse",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_client.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)
