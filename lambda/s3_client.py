"""S3 client operations for Quizify."""
import os
import boto3
from utils import generate_uuid, get_file_extension


s3_client = boto3.client('s3')

UPLOADS_BUCKET = os.environ.get('UPLOADS_BUCKET', '')


def download_file(bucket: str, key: str, local_path: str) -> str:
    """Download a file from S3 to local path."""
    s3_client.download_file(bucket, key, local_path)
    return local_path


def download_file_to_tmp(bucket: str, key: str) -> str:
    """Download a file from S3 to /tmp directory."""
    filename = key.split('/')[-1]
    local_path = f'/tmp/{filename}'
    return download_file(bucket, key, local_path)


def generate_presigned_url(filename: str, expiration: int = 3600) -> dict:
    """Generate a presigned URL for uploading a file to S3.

    Returns:
        dict with upload_url, upload_id, and s3_key
    """
    upload_id = generate_uuid()
    extension = get_file_extension(filename)

    # Store files with upload_id prefix for easy tracking
    s3_key = f"uploads/{upload_id}/{filename}"

    # Determine content type
    content_types = {
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'doc': 'application/msword',
        'txt': 'text/plain'
    }
    content_type = content_types.get(extension, 'application/octet-stream')

    url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': UPLOADS_BUCKET,
            'Key': s3_key,
            'ContentType': content_type
        },
        ExpiresIn=expiration
    )

    return {
        'upload_url': url,
        'upload_id': upload_id,
        's3_key': s3_key
    }


def get_object_content(bucket: str, key: str) -> bytes:
    """Get the content of an S3 object as bytes."""
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response['Body'].read()
