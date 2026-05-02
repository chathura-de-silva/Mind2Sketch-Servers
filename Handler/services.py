import random

from config import imageStatus, jobType
from database import database
from models import ImageResponse
from redisClient import enqueue_job
from vectors import VECTOR_LENGTH
import asyncio


async def random_generator(count: int) -> list[ImageResponse]:
    
    async def create_one() -> ImageResponse:
        vector = [0] * VECTOR_LENGTH # place holder vector to create a database entry.

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
