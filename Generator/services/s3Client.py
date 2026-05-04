import boto3
from config import settings

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_default_region,
    **(
        {"endpoint_url": settings.aws_s3_endpoint_url}
        if settings.aws_s3_endpoint_url
        else {}
    ),
)  # Automatically reads other config from env vars named acccording to boto3 standards.


def upload_to_s3(bucket_name: str, file_data: bytes, object_key: str, content_type: str = f"image/{settings.image_content_type.value}") -> str:
    s3.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=file_data,
        ContentType=content_type,
    )
    return object_key