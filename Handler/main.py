from fastapi import FastAPI
from vectors import load_vectors
import vectors
from contextlib import asynccontextmanager
from database import database as dbClient
from api import router
from celeryQueue import celery_app

@asynccontextmanager
async def lifespan(app: FastAPI):

    vectors.fixedVectors = load_vectors()
    dbClient.connect()
    await dbClient.init_collections()
    yield
    celery_app.close()
    dbClient.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
