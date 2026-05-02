from fastapi import FastAPI
from vectors import load_vectors
from contextlib import asynccontextmanager
from database import database as dbClient
from redisClient import redis_conn
from api import router

@asynccontextmanager
async def lifespan(app: FastAPI):

    global vectors
    vectors = load_vectors()
    dbClient.connect()
    await dbClient.init_collections()
    yield 
    redis_conn.close()
    dbClient.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
