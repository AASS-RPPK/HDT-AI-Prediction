from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "ai_prediction",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    result_expires=86400,  # 24 hours
)

celery_app.autodiscover_tasks(["app.worker"])
