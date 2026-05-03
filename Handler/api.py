from fastapi import APIRouter, HTTPException
from services import mix_generator, random_generator, slide_editor, text_generator
from models import (
    ImageResponse, RandomGenerateRequest, SlideGenerateRequest, TextToImageRequest,
    MixGenerateRequest, TextEditRequest, ImagesResponse
)
from vectors import get_fixed_vectors

router = APIRouter()

@router.post("/images/random", response_model=ImagesResponse)
async def random_generate(body: RandomGenerateRequest):
    images = await random_generator(body.count)
    return ImagesResponse(images=images, count=len(images))

@router.post("/images/text-to-image", response_model=ImagesResponse)
async def text_generate(body: TextToImageRequest):
    images = await text_generator(body.prompt, body.count)
    return ImagesResponse(images=images, count=len(images))

@router.get("/images/text-edit", response_model=ImagesResponse)
async def text_edit(body: TextEditRequest):
    edited_images = ["edited_image_data"]
    return edited_images

@router.post("/images/slide", response_model=ImageResponse) # returns only one image.
async def slide_edit(body: SlideGenerateRequest):
    if body.vector_id > len(get_fixed_vectors()) - 1:
        raise HTTPException(status_code=422, detail=f"vector_id must be <= {len(get_fixed_vectors()) - 1}")
    try:
        new_image_id = await slide_editor(body.id, body.vector_id, body.blend_ratio)
        return ImageResponse(id=new_image_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e: 
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/images/mix", response_model=ImagesResponse)
async def mix_generate(body: MixGenerateRequest):
    if body.weights and len(body.weights) != len(body.image_ids):
        raise HTTPException(status_code=422, detail="Length of weights must match length of image_ids")
    try:
        images = await mix_generator(body.image_ids, body.count, body.weights)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return ImagesResponse(images=images, count=len(images))

