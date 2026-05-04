from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict

class ImageFormat(Enum):
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"

class Settings(BaseSettings):
     # Redis Settings
    redis_host: str = ""
    redis_port: int = 0
    redis_password: str = ""
    redis_gen_queue: str = ""
    redis_preproc_queue: str = ""

    # S3 Settings
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_bucket_name: str = ""
    aws_default_region: str = "us-east-1"
    s3_image_file_type: ImageFormat = ImageFormat.PNG
    image_expiration_seconds: int = 3600 # how long the presigned upload url is valid for, in seconds

    aws_s3_endpoint_url: str = ""  # Optional, for custom S3-compatible services

    #Databse Settings
    mongodb_uri: str = ""
    mongodb_db_name: str = ""

    # Automatically load from .env file
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()


class jobType(Enum): # for communicating the type of job to the workers via redis queues
    GENERATE_S = 1
    GENERATE_W = 2
    PRE_MIX = 3
    PRE_MAPPER_TEXT_INIT = 4
    PRE_MAPPER_TEXT_EDIT = 5
    PRE_MAPPER_RAND = 6


class imageStatus(Enum):
    PENDING = "pending" # if its on the pre processing queue
    QUEUED = "queued" # if its on the generation queue
    READY = "ready" # if its ready to be displayed
    RUNNING = "running" # if its currently being processed picked from generation queue
    FAILED = "failed" # if its processing failed

class ChangeType(Enum): # for tracking the image history in the database
    TEXT_INIT   = "text_init"
    TEXT_EDIT   = "text_edit"
    SLIDE_EDIT  = "slide_edit"
    RANDOM_INIT = "random_init"
    MIX         = "mix"