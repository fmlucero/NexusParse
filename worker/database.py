import os
import json
import logging
import psycopg2
from psycopg2.extras import Json

logger = logging.getLogger("NexusParse.Worker.DB")
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Returns a psycopg2 connection object."""
    if not DATABASE_URL:
        logger.warning("DATABASE_URL is not set. Assuming test environment without DB.")
        return None
    return psycopg2.connect(DATABASE_URL)

def save_extraction_to_db(user_id: str, original_file_reference: str, extracted_data: dict):
    """
    Saves the AI extracted payload into Postgres.
    Uses Context Managers to ensure correct connection closing
    and prevents memory leaks or dangling transactions.
    """
    conn = get_db_connection()
    if not conn:
        return
        
    try:
        # Context manager for automatic commit/rollback
        with conn:
            with conn.cursor() as cur:
                # We use psycopg2.extras.Json to seamlessly map dicts to PostgreSQL JSONB
                query = """
                    INSERT INTO extractions (user_id, original_file_reference, extracted_data)
                    VALUES (%s, %s, %s)
                    RETURNING extraction_id;
                """
                cur.execute(query, (user_id, original_file_reference, Json(extracted_data)))
                row = cur.fetchone()
                
                logger.info(f"Successfully committed payload to Database. Extraction ID: {row[0]}")
    except Exception as e:
        logger.error(f"Failed to persist extraction to Database: {e}")
        # We re-raise to trigger the Celery Retry Backoff
        raise e
    finally:
        conn.close()
