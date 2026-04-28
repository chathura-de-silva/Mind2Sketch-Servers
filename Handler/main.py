from fastapi import FastAPI
from services import random_generator
from vectors import load_vectors

vectors = load_vectors()
app = FastAPI()

@app.post("/random")
def random_generate(count: int):
    images = random_generator(count)
    return images

