from celery import Celery
from config import jobType, settings

celery_app = Celery(
    "ml_jobs",
    broker=f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/0",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    task_track_started=True,
       task_queues={
        settings.redis_preproc_queue: {"exchange": settings.redis_preproc_queue}
    },
    task_default_queue=settings.redis_preproc_queue,
)

def enqueue_job(job_type: jobType, payload: dict, job_id: str) -> str:

    full_job_id = "job_" + job_id

    celery_app.send_task(
        job_type.value,       
        kwargs=payload,
        task_id=full_job_id,
        queue=settings.redis_gen_queue,       
    )

    return full_job_id