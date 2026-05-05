from celeryQueue import celery_app, enqueue_job
from config import jobType
from model.model import model_manager

@celery_app.task(name=jobType.PRE_MAPPER_RAND.value, bind=True, max_retries=2)
def rand_style_vector_generator(self, **kwargs):
    job_id = self.request.id.replace("job_", "")
    # remove the job_ prefix to get the actual image_id
    try:
        seed = kwargs.get("seed")
        if seed is None:
            raise ValueError("Seed value is required for generating style vector.")
        
        style_vector = model_manager.random_z_to_s(seed)
        enqueue_job(
            job_type=jobType.GENERATE_S,
            payload={"vector": style_vector},
            job_id=job_id,
        )

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)