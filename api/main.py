import logging
from fastapi import FastAPI
from routes import extraction

# Setup structured logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger("NexusParse.API")

app = FastAPI(
    title="NexusParse API Gateway",
    description="Asynchronous AI Extraction Fleet Gateway",
    version="1.0.0"
)

# Include Routers
app.include_router(extraction.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("API Gateway starting up...")

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "api-gateway"}
