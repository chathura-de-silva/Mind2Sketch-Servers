from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated

from config import ImageStatus
from models import (
    SingleImageGetResponse,
    SingleImageGetRequest,
    InitialFacesRequest,
    InitialFacesResponse,
    InitialFaceItem,
    UploadUrlResponse,
)
from services import get_image_by_id, get_initial_faces, get_presigned_upload_url

router = APIRouter()


@router.get("/initial-faces", response_model=InitialFacesResponse)
async def get_initial_faces_route(params: Annotated[InitialFacesRequest, Query()]):
    try:
        items = await get_initial_faces(params.gender, params.age)
    except ConnectionError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return InitialFacesResponse(items=[InitialFaceItem(**item) for item in items])


@router.get("/images/{id}", response_model=SingleImageGetResponse)
async def get_image(params: SingleImageGetRequest = Depends()):
    try:
        image_data = await get_image_by_id(params.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=500, detail=str(e))
    if image_data["status"] != ImageStatus.READY.value:
        raise HTTPException(
            status_code=202,
            detail=f"Image is not ready yet. Current status: {image_data['status']}",
        )
    return SingleImageGetResponse(
        id=params.id, url=image_data["url"], expires_in=image_data["expires_in"]
    )

@router.post("/images/upload")
async def get_upload_url():
    upload_url, download_url = await get_presigned_upload_url()
    return UploadUrlResponse(upload_url=upload_url, download_url=download_url)