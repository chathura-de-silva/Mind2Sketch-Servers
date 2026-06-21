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

    #Databse Settings
    mongodb_uri: str = ""
    mongodb_db_name: str = ""

    # Automatically load from .env file
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()


class jobType(Enum):
    GENERATE_S = "GENERATE_S"
    GENERATE_W = "GENERATE_W"
    PRE_MIX = "PRE_MIX"
    PRE_MAPPER_TEXT = "PRE_MAPPER_TEXT"
    PRE_MAPPER_RAND = "PRE_MAPPER_RAND"
    PRE_PROJECT_E4E = "PRE_PROJECT_E4E"


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