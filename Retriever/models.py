from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated

ImageId = Annotated[str, StringConstraints(pattern=r'^[a-f0-9]{24}$')]
class SingleImageGetRequest(BaseModel):
       id: ImageId = Field(..., description="ID of image to be retreived.")

class SingleImageGetResponse(BaseModel):
    id: ImageId = Field(..., description="ID of the image.")
    url: str = Field(..., description="URL to access the image.")
    expires_in: int = Field(..., description="Time in seconds until the URL expires.")