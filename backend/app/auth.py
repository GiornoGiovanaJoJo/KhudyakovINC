import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import hashlib
import hmac
from dotenv import load_dotenv

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme123")
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-fallback-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)


def _hash_password(password: str) -> str:
    """Simple SHA-256 hash for admin password comparison."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_admin(username: str, password: str) -> bool:
    if username != ADMIN_USERNAME:
        return False
    return hmac.compare_digest(
        _hash_password(password),
        _hash_password(ADMIN_PASSWORD),
    )


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        user_type: str = payload.get("type")
        if username is None or user_type != "admin":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or unauthorized")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id_str: str = payload.get("sub")
        # Check if it's a user (numeric sub) or admin (username)
        # For now, if it's numeric, we assume it's a user_id
        if user_id_str is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        return {"id": user_id_str, "sub": user_id_str}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security_optional),
) -> dict | None:
    if not credentials:
        return None
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            return None
        return {"id": user_id_str, "sub": user_id_str}
    except JWTError:
        return None
