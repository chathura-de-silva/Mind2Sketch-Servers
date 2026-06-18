from bson import ObjectId
from config import ImageStatus
from database import database
from config import settings
from s3Client import generate_presigned_download_url
from typing import Optional


async def get_initial_faces(gender: Optional[str], age: Optional[str]):
    query = {}
    if gender:
        query["gender"] = gender
    if age:
        query["age"] = age

    face_docs = await database.db.initial_faces.find(query).to_list(length=None)
    if not face_docs:
        return []

    results = []
    for doc in face_docs:
        image_id = doc["image_id"]
        try:
            url_data = generate_presigned_download_url(
                bucket_name=settings.s3_bucket_name,
                object_key=image_id,
            )
        except Exception as e:
            raise ConnectionError(f"Failed to generate presigned URL with S3: {str(e)}")
        results.append({"image_id": image_id, "url": url_data["url"]})

    return results


async def get_image_by_id(image_id: str):

    result = await database.db.images.find_one({"_id": ObjectId(image_id)})

    if result is None:
        raise ValueError("Image not found")
    if result.get("status") != ImageStatus.READY.value:
        return {
            "status": result.get("status"),
            "url": None,
            "expires_in": None,
        }  # Image is not ready yet, return null URL and expiration.

    try:
        url = generate_presigned_download_url(
            bucket_name=settings.s3_bucket_name,
            object_key=image_id,
        )
    except Exception as e:
        raise ConnectionError(f"Failed to generate presigned URL with S3: {str(e)}")

    return {
        "status": ImageStatus.READY.value,
        "url": url["url"],
        "expires_in": url["expires_in"],
    }
