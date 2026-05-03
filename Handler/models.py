from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated, List

# --- Request Models ---

class RandomGenerateRequest(BaseModel):
    count: int = Field(default=4, gt=0, le=25, description="Number of images to generate")

class TextToImageRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000, description="Image generation prompt")
    count: int = Field(default=4, gt=0, le=25, description="Number of images to generate")


ImageId = Annotated[str, StringConstraints(pattern=r'^[a-f0-9]{24}$')]
class MixGenerateRequest(BaseModel):
    image_ids: List[ImageId] = Field(..., min_length=2, description="IDs of images to mix")
    count: int = Field(default=4, gt=0, le=25, description="Number of mixed images to generate")
    weights : List[float] = Field(default_factory=list, description="Optional weights for each image in mixing")

class TextEditRequest(BaseModel):
    id: ImageId = Field(..., description="ID of image to edit")
    prompt: str = Field(..., min_length=1, max_length=500)
    count: int = Field(default=1, gt=0, le=25, description="Number of edited images to generate")

class SlideGenerateRequest(BaseModel):
     id: str = Field(..., description="ID of the starter image")
     vector_id: int = Field(..., ge=0, description="feature vector number for slide styles")
     blend_ratio: float = Field(default=0.5, ge=0.0, le=1.0)
     
# --- Response Models ---

class ImageResponse(BaseModel):
    id: str

class ImagesResponse(BaseModel):
    images: List[ImageResponse]
    count: int

