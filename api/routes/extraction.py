import logging
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from pydantic import BaseModel

from auth import verify_token
from celery_app import celery_client
from minio_client import upload_file_to_minio

router = APIRouter()
logger = logging.getLogger("NexusParse.API.Routes")

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

@router.post("/extract/", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED, tags=["Extraction"])
async def extract_pdf(
    file: UploadFile = File(...),
    token_payload: dict = Depends(verify_token)
):
    """
    1. Validates JWT Token
    2. Temp stores PDF on MinIO
    3. Triggers async worker task
    4. Returns 202 instantly
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Read file content safely
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file submitted.")
    
    # Store file to MinIO
    try:
        object_name = upload_file_to_minio(contents, file.filename)
        logger.info(f"File uploaded to MinIO successfully: {object_name}")
    except Exception as e:
        logger.error(f"Failed to upload file to MinIO: {e}")
        raise HTTPException(status_code=500, detail="Storage failure. Please try again later.") from e
    
    # Submit task to Celery
    try:
        # Pushing the task ID to Celery. Make sure task signature matches exactly what is expected.
        # "tasks.process_extraction" will be the worker function
        user_id = token_payload.get("sub", "unknown")
        task = celery_client.send_task(
            "tasks.process_extraction",
            kwargs={"object_name": object_name, "user_id": user_id}
        )
        logger.info(f"Dispatched task to Celery: {task.id}")
        
    except Exception as e:
        logger.error(f"Celery failed to accept task: {e}")
        raise HTTPException(status_code=500, detail="Broker failure. Please try again later.") from e
    
    return TaskResponse(
        task_id=task.id,
        status="PROCESSING",
        message="PDF successfully queued for extraction."
    )

@router.get("/task/{task_id}", tags=["Extraction"])
def get_task_status(task_id: str, token_payload: dict = Depends(verify_token)):
    """
    Poller for clients to check their extraction status.
    """
    res = celery_client.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": res.status,
        "result": res.result if res.ready() else None
    }
