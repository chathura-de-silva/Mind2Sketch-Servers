from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    redis_host: str = ""
    redis_port: int = 0
    redis_password: str = ""
    redis_gen_queue: str = ""
    redis_preproc_queue: str = ""

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings() 


class jobType(Enum):
    GENERATE_S = "GENERATE_S"
    GENERATE_W = "GENERATE_W"
    PRE_MIX = "PRE_MIX"
    PRE_MAPPER_TEXT_INIT = "PRE_MAPPER_TEXT_INIT"
    PRE_MAPPER_TEXT_EDIT = "PRE_MAPPER_TEXT_EDIT"
    PRE_MAPPER_RAND = "PRE_MAPPER_RAND"
