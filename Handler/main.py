from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    await vectors.load_face_vectors()
    yield
    celery_app.close()
    dbClient.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
