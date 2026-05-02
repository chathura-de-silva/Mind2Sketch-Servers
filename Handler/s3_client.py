import boto3
from urllib.request import Request, urlopen
from config import settings

s3 = boto3.client('s3',
				  aws_access_key_id= settings.aws_access_key_id,
                  aws_secret_access_key= settings.aws_secret_access_key,
                    region_name= settings.aws_default_region,   
                     **({'endpoint_url': settings.aws_s3_endpoint_url} if settings.aws_s3_endpoint_url else {}
                  )  # Automatically reads other config from env vars named acccording to boto3 standards.


def generate_presigned_upload_url(bucket_name, object_name, content_type='image/png', expiration=3600):
	presigned_url = s3.generate_presigned_url(
		'put_object',
		Params={
			'Bucket': bucket_name,
			'Key': object_name,
			'ContentType': content_type,
		},
		ExpiresIn=expiration,
	)
	return {
		'url': presigned_url,
		'key': object_name,
	}
