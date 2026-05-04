from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict

class ImageType(str, Enum):
    PNG = "png"
    JPEG = "jpeg"
    JPG = "webp"

class Settings(BaseSettings):
    redis_host: str = ""
    redis_port: int = 0
    redis_password: str = ""
    redis_gen_queue: str = ""

     # S3 Settings
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_bucket_name: str = ""
    aws_default_region: str = "us-east-1"
    image_content_type: ImageType = ImageType.PNG
    aws_s3_endpoint_url: str = ""  # Optional, for custom S3-compatible services


    #Databse Settings
    mongodb_uri: str = ""
    mongodb_db_name: str = ""


    model_config = SettingsConfigDict(env_file=".env")

settings = Settings() 


class jobType(Enum):
    GENERATE_S = "GENERATE_S"
    GENERATE_W = "GENERATE_W"
    PRE_MIX = "PRE_MIX"
    PRE_MAPPER_TEXT_INIT = "PRE_MAPPER_TEXT_INIT"
    PRE_MAPPER_TEXT_EDIT = "PRE_MAPPER_TEXT_EDIT"
    PRE_MAPPER_RAND = "PRE_MAPPER_RAND"


class ImageStatus(Enum):
    PENDING = "pending" # if its on the pre processing queue
    QUEUED = "queued" # if its on the generation queue
    READY = "ready" # if its ready to be displayed
    RUNNING = "running" # if its currently being processed picked from generation queue
    FAILED = "failed" # if its processing failed