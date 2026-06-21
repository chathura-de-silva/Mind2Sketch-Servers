import io
import requests
from PIL import Image
from celeryQueue import celery_app, enqueue_job
from config import jobType
from model.model import model_manager

@celery_app.task(name=jobType.PRE_PROJECT_E4E.value, bind=True, max_retries=2)
def project_and_generate(self, **kwargs):
    image_id = self.request.id.replace("job_", "")
    image_url = kwargs.get("image_url")
    try:
        if image_url is None:
            raise ValueError("Image URL is required for E4E projection.")

        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content)).convert("RGB")

        face_img = model_manager.detect_crop_and_resize(image)
        # Call the E4E projection function to get the W+ vector
        w_plus_vector = model_manager.project_e4e(face_img)
        
        # Convert W+ vector to Style Space
        style_vector = model_manager.w_plus_to_s(w_plus_vector)
        
        enqueue_job(
            job_type=jobType.GENERATE_S,
            payload={"vector": style_vector},
            job_id=image_id,
        )

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
   