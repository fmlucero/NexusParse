from fastapi.testclient import TestClient
import jwt
import datetime

# Mock some environment info to make sure the app initializes cleanly
import os
os.environ["REDIS_URL"] = "redis://localhost:6379/1"

from api.main import app
from api.auth import JWT_SECRET, ALGORITHM

client = TestClient(app)

def get_valid_token():
    payload = {"sub": "test-user", "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_extract_missing_token():
    # Attempt extraction without JWT
    # Using dummy file just to trigger the route
    response = client.post("/api/v1/extract/", files={"file": ("test.pdf", b"%PDF-1.4", "application/pdf")})
    assert response.status_code == 403 # HTTPBearer defaults to 403

def test_extract_invalid_token():
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.post("/api/v1/extract/", headers=headers, files={"file": ("test.pdf", b"%PDF-1.4", "application/pdf")})
    assert response.status_code == 401
