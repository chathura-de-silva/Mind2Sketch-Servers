from celeryQueue import celery_app
from config import jobType, settings, ImageStatus
from model.model import model_manager
from services.database import update_image_status
from services.s3Client import upload_to_s3


@celery_app.task(name=jobType.GENERATE_W.value, bind=True, max_retries=2)
def handle_generate_w(self, **kwargs):   
    # Not implemented. Following is the boilerplate. Currently the synthesis service only supports generation from style space.  
    return
    job_id = self.request.id.replace("job_", "")
    try:
        update_image_status(job_id, ImageStatus.RUNNING.value)
        w_vector = kwargs.get("vector", [])

        if not w_vector:
            raise ValueError("No vector provided for GENERATE_W task")
        
        image = model_manager.predict_w(w_vector)
        upload_to_s3(settings.s3_bucket_name, image, job_id)
        update_image_status(job_id, ImageStatus.READY.value)

    except Exception as exc:
        update_image_status(job_id, ImageStatus.FAILED.value)
        raise self.retry(exc=exc, countdown=5)
