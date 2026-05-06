from celeryQueue import celery_app, enqueue_job
from config import jobType
from style_mixer import style_mixer

@celery_app.task(name=jobType.PRE_MIX.value, bind=True, max_retries=2)
def mix_styles(self, **kwargs):
    # remove the job_ prefix to get the actual image_id
    try:
        vectors = kwargs.get("image_vectors")
        weights = kwargs.get("weights")
        count = kwargs.get("count")
        new_image_ids = kwargs.get("new_image_ids")

        if vectors is None or count is None or new_image_ids is None:
            raise ValueError("Required parameters for style mixing are missing.")
        
        new_style_vectors = style_mixer(vectors, weights, count)
        
        for new_vector, new_image_id in zip(new_style_vectors, new_image_ids):
            enqueue_job(
                job_type=jobType.GENERATE_S,
                payload={"vector": new_vector},
                job_id=new_image_id,
            )

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)