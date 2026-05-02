import random

from bson import ObjectId
from config import imageStatus, jobType
from database import database
from models import ImageResponse
from redisClient import enqueue_job
from vectors import VECTOR_LENGTH, get_fixed_vectors
import asyncio
import numpy as np

async def random_generator(count: int) -> list[ImageResponse]:
    
    async def create_one() -> ImageResponse:
        vector = [0.0] * VECTOR_LENGTH # place holder vector to create a database entry.

        result = await database.db["images"].insert_one(
            {"vector": vector, "status": imageStatus.PENDING.value}
        )

        image_id = str(result.inserted_id)

        enqueue_job(
            job_type=jobType.PRE_MAPPER_RAND,
            payload={"seed":random.randint(-1000, 1000)},  # update the bounds as needed
            job_id=image_id
        )

        return ImageResponse(id=image_id)

    return list(await asyncio.gather(*[create_one() for _ in range(count)]))


def mix_generator():
    # This function generates mixed images and returns them as a list
    images = []
    for _ in range(5):  # Assuming we generate 5 mixed images
        image = "mixed_image_data"
        images.append(image)
    return images


def text_generator(prompt: str, count: int):
    # This function generates images based on text input and returns them as a list
    images = []
    for _ in range(count):
        image = f"text_to_image_data_{prompt}"
        images.append(image)
    return images


async def slide_editor(image_id: str, vector_id: int, blend_ratio: float)-> str:

    image_entry = await database.db["images"].find_one({"_id": ObjectId(image_id)})
    if image_entry is None:
        raise ValueError(f"Image with id {image_id} does not exist")   
    if image_entry["status"] != imageStatus.READY.value:
        raise ValueError(f"Image with id {image_id} is not ready for editing. Current status: {image_entry['status']}")
    
    original_vector = np.array(image_entry["vector"])
    feature_vector= np.array(get_fixed_vectors()[vector_id]["vector"] )
    blended_vector = (original_vector + blend_ratio * feature_vector).tolist()
    result = await database.db["images"].insert_one(
        {"vector": blended_vector, "status": imageStatus.QUEUED.value}
    )
    new_id = str(result.inserted_id)
    enqueue_job(
        job_type=jobType.GENERATE_W,
        payload={"vector": blended_vector},
        job_id=new_id
    )
    return new_id