from celery import Celery
from config import settings

celery_app = Celery(
    "ml_jobs",
    broker=f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/0",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    task_track_started=True,
       task_queues={
        settings.redis_gen_queue: {"exchange": settings.redis_gen_queue}
    },
    task_default_queue=settings.redis_gen_queue,
)