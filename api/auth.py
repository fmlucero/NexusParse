import os
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-for-demo-purposes")
ALGORITHM = "HS256"

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Validates the given JWT token. 
    In a real-world scenario, you might also check scopes, expiration heavily, etc.
    """
    token = credentials.credentials
    try:
        # Require a valid JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e

# Demo utility for token generation (Not for production)
def create_demo_token(user_id: str):
    import datetime
    payload = {
        "sub": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
