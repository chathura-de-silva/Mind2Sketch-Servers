from celeryQueue import celery_app
from config import jobType
from model.model import model_manager
from services.database import update_image_status, update_image_vector_by_id
from services.s3Client import upload_to_s3
from config import settings, ImageStatus

@celery_app.task(name=jobType.GENERATE_S.value, bind=True, max_retries=2)
def handle_generate_s(self, **kwargs):
    job_id = self.request.id.replace("job_", "")
    # remove the job_ prefix to get the actual image_id
    try:
       update_image_status(job_id, ImageStatus.RUNNING.value)
       style_vector = kwargs.get("vector", [])

       if not style_vector:
            raise ValueError("No vector provided for GENERATE_S task")
       
       image = model_manager.predict_s(style_vector)
       upload_to_s3(settings.s3_bucket_name, image,job_id)
       update_image_status(job_id, ImageStatus.READY.value)
       update_image_vector_by_id(job_id, style_vector)

    except Exception as exc:
        update_image_status(job_id, ImageStatus.FAILED.value)
        raise self.retry(exc=exc, countdown=5)