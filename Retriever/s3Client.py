import boto3
from config import settings

s3 = boto3.client('s3',
				  aws_access_key_id= settings.aws_access_key_id,
                  aws_secret_access_key= settings.aws_secret_access_key,
                    region_name= settings.aws_default_region,   
                     **({'endpoint_url': settings.aws_s3_endpoint_url} if settings.aws_s3_endpoint_url else {})
                  )  # Automatically reads other config from env vars named acccording to boto3 standards.


def generate_presigned_download_url(bucket_name, object_key, expiration=3600):
    file_name = object_key + settings.image_file_extension
    presigned_url = s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket_name,
            'Key': file_name,
        },
        ExpiresIn=expiration,
    )
    return {
        'url': presigned_url,
        'expires_in': expiration,
    }

