import torch
from celeryQueue import celery_app, enqueue_job
from config import jobType
from model.model import model_manager

_NOISE_SCALE = 0.05


@celery_app.task(name=jobType.PRE_MAPPER_TEXT.value, bind=True, max_retries=2)
def text_edit(self, **kwargs):
    """handles both text-based initial generation and text-based editing.
    For generation from text, ground_vector will be set to neutral vector value and lambda_val will be set to 4.0(both are not expected inside job metadata) to create more relevant initial images.
    For editing existing images, ground_vector(original_vector) and lambda_val(blend_ratio) both are expected to be provided as job metadata.
    """ 
    try:
        text_prompt = kwargs.get("prompt")
        if text_prompt is None:
            raise ValueError("text_prompt is required.")

        try:
            negative_prompt = model_manager.get_negative_prompt(text_prompt)
        except Exception:
            negative_prompt = None
        style_direction = model_manager.text_to_style_direction(text_prompt, negative_prompt=negative_prompt)
        count = kwargs.get("count", 1)
        new_image_ids = kwargs.get("new_image_ids")
        if new_image_ids is None or len(new_image_ids) != count:
            raise ValueError("new_image_ids must be provided with length equal to count.")

        base_direction = torch.tensor(style_direction)
        noise_std = _NOISE_SCALE * base_direction.std()
        ground_vector = torch.tensor(kwargs.get("original_vector",model_manager.neutral_style_vector))
        lambda_val = kwargs.get("blend_ratio", 4.0) 
        vectors = [(base_direction*lambda_val+ground_vector).tolist()]
        for _ in range(count - 1):
            vectors.append(((base_direction + torch.randn_like(base_direction) * noise_std)*lambda_val+ground_vector).tolist())

        for vector, image_id in zip(vectors, new_image_ids):
            enqueue_job(
                job_type=jobType.GENERATE_S,
                payload={"vector": vector},
                job_id=image_id,
            )
    except ValueError:
        raise
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
