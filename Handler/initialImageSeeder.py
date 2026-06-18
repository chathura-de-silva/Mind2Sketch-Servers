from celeryQueue import enqueue_job
from config import imageStatus, jobType
from database import database

async def enqueue_face_generations(face_entries: list[dict]) -> list[str]:
    result = await database.db["images"].insert_many(
        [{"vector": entry["vector"], "status": imageStatus.QUEUED.value} for entry in face_entries]
    )
    image_ids = [str(oid) for oid in result.inserted_ids]
    for image_id, entry in zip(image_ids, face_entries):
        enqueue_job(
            job_type=jobType.GENERATE_S,
            payload={"vector": entry["vector"]},
            job_id=image_id,
        )
    return image_ids

async def is_initial_faces_seeded(expected_count: int) -> bool:
    existing = await database.db.list_collection_names()
    if "initial_faces" not in existing:
        return False
    actual_count = await database.db["initial_faces"].count_documents({})
    if actual_count != expected_count:
        await database.db.drop_collection("initial_faces")
        return False
    return True

async def create_and_seed_initial_face_collection(face_entries: list[dict]):
    # This function is used to create a separate collection for initial face images if needed
    # this collection has its own id as primary key.
    # other fields include a reference image_id which could be used to link back to the main images collection, gender, age.

    await database.db.create_collection(
        "initial_faces",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["image_id", "gender", "age"],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "image_id": {"bsonType": "string"},
                    "gender": {"bsonType": "string"},
                    "age": {"bsonType": "string"},
                },
            }
        },
    )

    await database.db["initial_faces"].insert_many(
        [
            {
                "image_id": entry["image_id"],
                "gender": entry["gender"],
                "age": entry["age"],
            }
            for entry in face_entries
        ]
    )
