from fastapi import APIRouter, Body
from services import mix_generator, random_generator, text_generator
from models import (
    ImageResponse, RandomGenerateRequest, SlideGenerateRequest, TextToImageRequest,
    MixGenerateRequest, TextEditRequest, ImagesResponse
)

router = APIRouter()

@router.post("/images/random", response_model=ImagesResponse)
def random_generate(body: RandomGenerateRequest):
    images = random_generator(count=body.count)
    return images

@router.post("/images/text-to-image", response_model=ImagesResponse)
def text_generate(body: TextToImageRequest):
    images = text_generator(body.prompt, body.count)
    return images

@router.get("/images/text-edit", response_model=ImagesResponse)
def text_edit(body: TextEditRequest):
    edited_images = ["edited_image_data"]
    return edited_images

@router.post("/images/slide", response_model=ImageResponse) # returns only one image.
def slide_generate(body: SlideGenerateRequest):
    # Implementation for slide generation
    pass

@router.post("/images/mix", response_model=ImagesResponse)
def mix_generate(body: MixGenerateRequest):
    images = mix_generator()
    return images

