from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated, List, Optional

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
    negative_prompt: Optional[str] = Field(default=None, max_length=500, description="Negative prompt; auto-generated from prompt if empty")
    count: int = Field(default=1, gt=0, le=25, description="Number of edited images to generate")
    blend_ratio: float = Field(default=4.0, ge=0.0, le=6.0, description="Strength of the edit")

class SlideGenerateRequest(BaseModel):
    id: ImageId = Field(..., description="ID of the starter image")
    vector_ids: List[Annotated[int, Field(ge=0)]] = Field( ..., description="Feature vector numbers for slide styles", min_length=1, max_length=3)
    blend_ratios: List[Annotated[float, Field(ge=0.0, le=6.0)]] = Field(default_factory=list, min_length=1, max_length=3)

# --- Response Models ---

class ImageResponse(BaseModel):
    id: ImageId

class ImagesResponse(BaseModel):
    images: List[ImageResponse]
    count: int

