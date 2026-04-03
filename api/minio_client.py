import os
import io
import uuid
from minio import Minio

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "password")
BUCKET_NAME = "nexusparse-pdfs"

# Initialize MinIO client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

def ensure_bucket_exists():
    if not minio_client.bucket_exists(BUCKET_NAME):
        minio_client.make_bucket(BUCKET_NAME)

def upload_file_to_minio(file_bytes: bytes, original_filename: str) -> str:
    ensure_bucket_exists()
    
    # Generate unique ID for this file
    file_idx = str(uuid.uuid4())
    extension = original_filename.split(".")[-1] if "." in original_filename else "pdf"
    object_name = f"{file_idx}.{extension}"
    
    file_stream = io.BytesIO(file_bytes)
    length = len(file_bytes)
    
    minio_client.put_object(
        BUCKET_NAME,
        object_name,
        file_stream,
        length,
        content_type="application/pdf"
    )
    
    return object_name
