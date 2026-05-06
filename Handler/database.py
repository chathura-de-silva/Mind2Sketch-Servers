from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import ChangeType, imageStatus, settings


class Database:
    client: AsyncIOMotorClient
    db: AsyncIOMotorDatabase

    def connect(self):
        self.client = AsyncIOMotorClient(settings.mongodb_uri)
        self.db = self.client[settings.mongodb_db_name]

    def close(self):
        self.client.close()

    async def init_collections(self):
        existing = await self.db.list_collection_names()

        # ── Image Collection ──────────────────────────────────────────
        if "images" not in existing:
            await self.db.create_collection(
                "images",
                validator={
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["status"],
                        "properties": {
                            "_id": {"bsonType": "objectId"},
                            "vector": {
                                "bsonType": "array",
                                "items": {"bsonType": "double"},
                            },
                            "status": {
                                "bsonType": "string",
                                "enum": [
                                   e.value for e in imageStatus
                                ],
                            },
                        },
                    }
                },
            )

        # ── Stage Collection ──────────────────────────────────────────
        if "sequences" not in existing:
            await self.db.create_collection(
                "sequences",
                validator={
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["initial_image", "stages"],
                        "properties": {
                            "_id": {"bsonType": "objectId"},
                            "initial_image": {"bsonType": "objectId"},
                            "stages": {
                                "bsonType": "array",
                                "items": {
                                    "bsonType": "object",
                                    "required": [
                                        "stage_no",
                                        "change_type",
                                        "resulting_image",
                                    ],
                                    "properties": {
                                        "stage_no": {"bsonType": "int"},
                                        "change_type": {
                                            "bsonType": "string",
                                            "enum": [
                                              e.value for e in ChangeType
                                            ],
                                        },
                                        "change_metadata": {
                                            "bsonType": "object"  # flexible, varies per change_type
                                        },
                                        "resulting_image": {"bsonType": "objectId"},
                                    },
                                },
                            },
                        },
                    }
                },
            )

        # ── Generation Collection ─────────────────────────────────────
        if "generations" not in existing:
            await self.db.create_collection(
                "generations",
                validator={
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["meta_data", "initial_data", "image_stages"],
                        "properties": {
                            "_id": {"bsonType": "objectId"},
                            "meta_data": {"bsonType": "object"},
                            "initial_data": {"bsonType": "object"},
                            "image_sequences": {
                                "bsonType": "array",
                                "items": {"bsonType": "objectId"},
                            },
                        },
                    }
                },
            )

database = Database()
