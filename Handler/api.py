from fastapi import APIRouter, Body
from services import mix_generator, random_generator, text_generator

router = APIRouter()

@router.post("/random")
def random_generate(count: int = Body(..., embed=True)):
    images = random_generator(count)
    return images

@router.post("/mix")
def mix_generate():
    images = mix_generator()
    return images

@router.post("/texttoimage")
def text_generate():
    images = text_generator()
    return images