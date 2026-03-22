import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.hash import bcrypt
from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse, LoginRequest, TokenResponse
from ..auth import create_access_token, verify_admin
from ..deps import require_role
from ..models import UserRole
import hashlib

logger = logging.getLogger(__name__)

router = APIRouter()

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash. Supports bcrypt and legacy SHA-256 fallback."""
    # Check if it's a bcrypt hash (starts with $2b$ or $2a$)
    if hashed_password.startswith(("$2b$", "$2a$", "$2y$")):
        return bcrypt.verify(plain_password, hashed_password)
    # Legacy fallback: SHA-256 (for existing users before migration)
    legacy_hash = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return legacy_hash == hashed_password


@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(require_role([UserRole.ADMIN]))
):
    """Register a new user. Admin-only."""
    # Check if user already exists
    result = await db.execute(select(User).where(User.phone == user_in.phone))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Пользователь с таким номером уже существует")
    
    db_user = User(
        phone=user_in.phone,
        password_hash=hash_password(user_in.password),
        full_name=user_in.full_name,
        email=user_in.email,
        telegram=user_in.telegram,
        role=user_in.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # 1. Check if it's an admin login
    if verify_admin(login_data.username, login_data.password):
        access_token = create_access_token(data={"sub": login_data.username, "type": "admin"})
        return {"access_token": access_token, "token_type": "bearer", "user_type": "admin"}

    # 2. Otherwise check for regular user
    result = await db.execute(select(User).where(User.phone == login_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    access_token = create_access_token(data={"sub": str(user.id), "type": "user"})
    return {"access_token": access_token, "token_type": "bearer", "user_type": "user"}
