from redis import Redis
import json
from config import settings
from services import jobType


redis_conn = Redis( host= settings.redis_host,
    port=int(settings.redis_port),
    decode_responses=True,
    password=settings.redis_password,)

def enqueue_job(job_type: jobType, payload: dict, job_id: int) -> str:
    job = {
        "id": str(job_id),
        "type": job_type.value,
        "payload": payload
    }
    if job_type == jobType.GENERATE:
        redis_conn.rpush(settings.redis_gen_queue, json.dumps(job))
    else:
        redis_conn.rpush(settings.redis_preproc_queue, json.dumps(job))
    return job["id"]
