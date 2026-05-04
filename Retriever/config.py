from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # S3 Settings
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_bucket_name: str = ""
    aws_default_region: str = "us-east-1"

    aws_s3_endpoint_url: str = ""  # Optional, for custom S3-compatible services
    image_expiration_seconds: int = 3600 # Time in seconds until the generated image URL expires.
    image_file_extension: str = ".png"

    #Databse Settings
    mongodb_uri: str = ""  # better to use a read only user for this with limited permissions as the service is only for image retreival.
    mongodb_db_name: str = ""

    # Automatically load from .env file
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

class ImageStatus(Enum):
    PENDING = "pending" # if its on the pre processing queue
    QUEUED = "queued" # if its on the generation queue
    READY = "ready" # if its ready to be displayed
    RUNNING = "running" # if its currently being processed picked from generation queue
    FAILED = "failed" # if its processing failed