from minio import Minio
import io
from datetime import timedelta

from fastapi import HTTPException, UploadFile

from app.core.settings import get_settings


settings = get_settings()

minio_client = Minio(settings.MINIO_ENDPOINT,
               settings.MINIO_ROOT_USER,
               settings.MINIO_ROOT_PASSWORD,
               secure=True)

def ensure_bucket_exists(bucket_name: str):
    if not  minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        #print(f"Created bucket: {bucket_name}")


async def upload_file_to_minio(bucket_name: str, object_name: str, file: UploadFile):
    ensure_bucket_exists(bucket_name)
    content = await file.read()
    file.file.seek(0)
    minio_client.put_object(
        bucket_name,
        object_name,
        io.BytesIO(content),
        length=len(content),
        content_type=file.content_type
    )

    stat = minio_client.stat_object(bucket_name, object_name)

    return {
        "bucket_name": bucket_name,
        "object_name": object_name,
        "etag": stat.etag,
        "version_id": getattr(stat, "version_id", None),
        "file_name": file.filename
    }


async def generate_presigned_url(bucket_name: str, object_name: str, expiry: int = 3600) -> str:
    try:
        ensure_bucket_exists(bucket_name)
        url = minio_client.presigned_get_object(
            bucket_name,
            object_name,
            expires=timedelta(seconds=expiry)
        )
        return url
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate download link.")
