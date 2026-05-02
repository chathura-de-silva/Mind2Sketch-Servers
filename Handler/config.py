from pydantic_settings import BaseSettings, SettingsConfigDict

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

    aws_s3_endpoint_url: str = ""  # Optional, for custom S3-compatible services

    #Databse Settings
    mongodb_uri: str = ""
    mongodb_db_name: str = ""

    # Automatically load from .env file
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
