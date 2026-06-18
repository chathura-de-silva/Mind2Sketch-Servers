from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing import Annotated, Literal, Optional, List

ImageId = Annotated[str, StringConstraints(pattern=r'^[a-f0-9]{24}$')]

class SingleImageGetRequest(BaseModel):
       id: ImageId = Field(..., description="ID of image to be retreived.")

class SingleImageGetResponse(BaseModel):
    id: ImageId = Field(..., description="ID of the image.")
    url: str = Field(..., description="URL to access the image.")
    expires_in: int = Field(..., description="Time in seconds until the URL expires.")

class InitialFacesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    gender: Optional[Literal["male", "female"]] = Field(None, description="Filter by gender.")
    age: Optional[Literal["middle", "old", "young"]] = Field(None, description="Filter by age group.")

class InitialFaceItem(BaseModel):
    image_id: str = Field(..., description="ID of the image.")
    url: str = Field(..., description="Presigned URL to access the image.")

class InitialFacesResponse(BaseModel):
    items: List[InitialFaceItem]