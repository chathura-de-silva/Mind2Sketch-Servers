from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

dbClient = AsyncIOMotorClient(settings.mongodb_url)
db = dbClient[settings.mongodb_db_name]