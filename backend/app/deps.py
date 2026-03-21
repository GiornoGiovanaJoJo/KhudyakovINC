from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from .auth import security, JWT_SECRET, JWT_ALGORITHM
from .database import get_db
from .models import User, UserRole

async def get_current_active_user(
    credentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_type = payload.get("type")
        sub = payload.get("sub")
        
        if user_type == "admin":
            # Это супер-админ из .env
            return {"id": 0, "role": "admin", "is_superadmin": True}
        
        user_id = int(sub)
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(allowed_roles: list[str]):
    async def role_checker(user = Depends(get_current_active_user)):
        if isinstance(user, dict) and user.get("is_superadmin"):
            return user  # Superyadmin is allowed everything
        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Недостаточно прав (Not enough permissions)")
        return user
    return role_checker
