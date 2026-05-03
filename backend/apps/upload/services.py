import os
import json
import uuid
from minio import Minio

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
BUCKET_NAME = "jiaoge"


def get_minio_client() -> Minio:
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )


def ensure_bucket():
    client = get_minio_client()
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME)
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{BUCKET_NAME}/*"],
                }
            ],
        }
        client.set_bucket_policy(BUCKET_NAME, json.dumps(policy))


def upload_file(file_data, file_name: str, category: str = "general") -> str:
    ext = file_name.rsplit(".", 1)[-1] if "." in file_name else "bin"
    object_name = f"{category}/{uuid.uuid4().hex}.{ext}"
    client = get_minio_client()
    file_bytes = file_data.read()
    from io import BytesIO
    client.put_object(
        BUCKET_NAME, object_name, BytesIO(file_bytes),
        length=len(file_bytes),
        content_type=file_data.content_type if hasattr(file_data, "content_type") else "application/octet-stream",
    )
    return f"http://{MINIO_ENDPOINT}/{BUCKET_NAME}/{object_name}"


def delete_file(object_name: str):
    client = get_minio_client()
    client.remove_object(BUCKET_NAME, object_name)
