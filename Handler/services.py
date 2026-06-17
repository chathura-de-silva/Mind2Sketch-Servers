import random
from bson import ObjectId
from config import imageStatus, jobType
from database import database
from models import ImageResponse
from celeryQueue import enqueue_job
from vectors import get_fixed_vectors
import asyncio
import numpy as np


async def random_generator(count: int) -> list[ImageResponse]: # multiple jobs per invocation, one job per image - pre processing queue

    async def create_one() -> ImageResponse:
        result = await database.db["images"].insert_one(
            { "status": imageStatus.PENDING.value}
        )

        image_id = str(result.inserted_id)

        enqueue_job(
            job_type=jobType.PRE_MAPPER_RAND,
            payload={
                "seed": random.randint(-1000, 1000)
            },  # update the bounds as needed
            job_id=image_id,
        )

        return ImageResponse(id=image_id)

    return list(await asyncio.gather(*[create_one() for _ in range(count)]))


async def mix_generator( image_ids: list[str], count: int, weights: list[float]) -> list[ImageResponse]: # one job per invocation - pre processing queue
    image_vectors = []
    for image_id in image_ids:
        image_entry = await database.db["images"].find_one({"_id": ObjectId(image_id)})
        if image_entry is None:
            raise ValueError(f"Image with id {image_id} does not exist")
        if image_entry["status"] != imageStatus.READY.value:
            raise ValueError(
                f"Image with id {image_id} is not ready for mixing. Current status: {image_entry['status']}"
            )
        image_vectors.append(image_entry["vector"])
    status_updates = [
        { "status": imageStatus.PENDING.value}
        for _ in range(count)
    ]

    result = await database.db["images"].insert_many(status_updates)

    new_image_ids = [str(id) for id in result.inserted_ids]

    enqueue_job(
        job_type=jobType.PRE_MIX,
        payload={"image_vectors": image_vectors, "weights": weights, "count": count, "new_image_ids": new_image_ids},
        job_id= new_image_ids[0],  # Using the first image ID as the job ID for tracking
    )
    return [ImageResponse(id=image_id) for image_id in new_image_ids]


async def text_generator(prompt: str, count: int) -> list[ImageResponse]:  # one job per invocation - pre processing queue
    status_updates = [
        {"status": imageStatus.PENDING.value}
        for _ in range(count)
    ]

    result = await database.db["images"].insert_many(status_updates)
    image_ids = [str(id) for id in result.inserted_ids]

    enqueue_job(
        job_type=jobType.PRE_MAPPER_TEXT,
        payload={"prompt": prompt, "new_image_ids": image_ids, "count": count},
        job_id=image_ids[0],  # Using the first image ID as the job ID for tracking
    )

    return [ImageResponse(id=image_id) for image_id in image_ids]


async def slide_editor(image_id: str, vector_ids: list[int], blend_ratios: list[float]) -> str: #one job per invocation/image - generator queue

    image_entry = await database.db["images"].find_one({"_id": ObjectId(image_id)})
    if image_entry is None:
        raise ValueError(f"Image with id {image_id} does not exist")
    if image_entry["status"] != imageStatus.READY.value:
        raise ValueError(
            f"Image with id {image_id} is not ready for editing. Current status: {image_entry['status']}"
        )

    original_vector = np.array(image_entry["vector"],dtype=float)
    feature_vectors = np.array([get_fixed_vectors()[vid]["vector"] for vid in vector_ids], dtype=float)
    blended_vector = (original_vector + np.array(blend_ratios,dtype=float)@feature_vectors).tolist()

    result = await database.db["images"].insert_one(
        {"vector": blended_vector, "status": imageStatus.QUEUED.value}
    )
    new_id = str(result.inserted_id)
    enqueue_job(
        job_type=jobType.GENERATE_S, payload={"vector": blended_vector}, job_id=new_id
    )
    return new_id

async def text_editor(image_id: str, prompt: str, count: int, blend_ratio: float) -> list[ImageResponse]: #one job per invocation/image - pre processing queue

    image_entry = await database.db["images"].find_one({"_id": ObjectId(image_id)})
    if image_entry is None:
        raise ValueError(f"Image with id {image_id} does not exist")
    if image_entry["status"] != imageStatus.READY.value:
        raise ValueError(
            f"Image with id {image_id} is not ready for editing. Current status: {image_entry['status']}"
        )

    original_vector = image_entry["vector"]

    status_updates = [
        {"status": imageStatus.PENDING.value}
        for _ in range(count)
    ]

    result = await database.db["images"].insert_many(status_updates)

    new_image_ids = [str(id) for id in result.inserted_ids]

    enqueue_job(
        job_type=jobType.PRE_MAPPER_TEXT,
        payload={"prompt": prompt, "original_vector": original_vector, "blend_ratio": blend_ratio, "new_image_ids": new_image_ids, "count": count},
        job_id=new_image_ids[0],  # Using the first image ID as the job ID for tracking
    )

    return [ImageResponse(id=image_id) for image_id in new_image_ids]