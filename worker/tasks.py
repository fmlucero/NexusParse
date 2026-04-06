import os
import json
import logging
from celery import shared_task
from pydantic import ValidationError

from minio_client import get_file_from_minio
from llm_chains import extract_text_from_pdf, run_extraction_chain
from database import save_extraction_to_db

logger = logging.getLogger("NexusParse.Worker.Tasks")

@shared_task(
    name="tasks.process_extraction",
    bind=True,
    max_retries=3,
    default_retry_delay=10 # Base delay, overridden in backoff
)
def process_extraction(self, object_name: str, user_id: str):
    """
    1. Downloads PDF from MinIO
    2. Extracts text
    3. Runs Langchain + Pydantic extraction
    4. Handles AI hallucination / validation errors with auto-retry
    """
    logger.info(f"Task Started - Object: {object_name} | User: {user_id}")
    
    local_pdf = f"/tmp/{object_name}"
    
    try:
        # Step 1: Download
        logger.info("Downloading file from storage...")
        get_file_from_minio(object_name, local_pdf)
        
        # Step 2: Extract
        logger.info("Parsing PDF chunks...")
        raw_text = extract_text_from_pdf(local_pdf)
        
        if not raw_text.strip():
            raise ValueError("Parsed PDF is empty or contains no extractable text.")
            
        # Step 3: Run LLM Chain
        logger.info("Executing Chain...")
        extracted_data = run_extraction_chain(raw_text)
        
        logger.info(f"Successfully extracted: {json.dumps(extracted_data)[:100]}...")
        
        # Step 4: Save strictly modeled data to Postgres
        logger.info("Persisting validated schema into Database JSONB store...")
        save_extraction_to_db(
            user_id=user_id, 
            original_file_reference=object_name, 
            extracted_data=extracted_data
        )
        
        return {
            "status": "success",
            "extracted": extracted_data
        }

    except ValidationError as e:
        # The LLM output did not match the strict constraints. We trigger Retry Backoff.
        logger.warning(f"Pydantic Validation failed (Hallucination detected). Retrying... Error: {str(e)}")
        # Exponential backoff on JSON schema mismatches
        delay = self.default_retry_delay * (2 ** self.request.retries) 
        raise self.retry(exc=e, countdown=delay) from e

    except Exception as e:
        logger.error(f"Critical Worker Error: {e}", exc_info=True)
        # We might not retry on pure fatal errors (like minio offline) unless we want to,
        # but let's assume we do for robustness.
        raise self.retry(exc=e) from e
        
    finally:
        # Cleanup
        if os.path.exists(local_pdf):
            os.remove(local_pdf)
