from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import settings


class Database:
    client: AsyncIOMotorClient
    db: AsyncIOMotorDatabase

    def connect(self):
        self.client = AsyncIOMotorClient(settings.mongodb_uri)
        self.db = self.client[settings.mongodb_db_name]

    def close(self):
        self.client.close()

database = Database()
