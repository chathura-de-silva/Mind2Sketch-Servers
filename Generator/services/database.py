from bson import ObjectId
from pymongo import MongoClient
from config import settings

client = MongoClient(settings.mongodb_uri)
db = client[settings.mongodb_db_name]
images = db["images"]


def update_image_status(image_id: str, status: str):
    images.update_one(
        {"_id": ObjectId(image_id)},
        {"$set": {"status": status}}
    )

def update_image_vector_by_id(image_id: str, vector: list):
    images.update_one(
        {"_id": ObjectId(image_id)},
        {"$set": {"vector": vector}}
    )