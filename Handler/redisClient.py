from redis import Redis
import json
from dotenv import load_dotenv
import os

from services import jobType

load_dotenv()

redis_conn = Redis( host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "13963")),
    decode_responses=True,
    password=os.getenv("REDIS_PASSWORD"),)

generator_queue = os.getenv("REDIS_GEN_QUEUE", "generator_queue")  
preprocessing_queue = os.getenv("REDIS_PREPROC_QUEUE", "preprocessor_queue") 

def enqueue_job(job_type: jobType, payload: dict, job_id: int) -> str:
    job = {
        "id": str(job_id),
        "type": job_type.value,
        "payload": payload
    }
    if job_type == jobType.GENERATE:
        redis_conn.rpush(generator_queue, json.dumps(job))
    else:
        redis_conn.rpush(preprocessing_queue, json.dumps(job))
    return job["id"]
