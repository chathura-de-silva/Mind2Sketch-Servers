from fastapi import APIRouter, Depends, HTTPException

from config import ImageStatus
from models import  SingleImageGetResponse, SingleImageGetRequest
from services import get_image_by_id

router = APIRouter()

@router.get("/images/{id}", response_model=SingleImageGetResponse)
async def get_image(params: SingleImageGetRequest = Depends()):
    try:
        image_data = await get_image_by_id(params.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=500, detail=str(e))
    if image_data["status"] != ImageStatus.READY.value:
        raise HTTPException(status_code=202, detail=f"Image is not ready yet. Current status: {image_data['status']}") 
    return SingleImageGetResponse(
        id=params.id, url=image_data["url"], expires_in=image_data["expires_in"]
    )
