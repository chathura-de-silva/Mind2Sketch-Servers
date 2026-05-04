from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import database as dbClient
from api import router


@asynccontextmanager
async def lifespan(app: FastAPI):

    dbClient.connect()
    yield
    dbClient.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
