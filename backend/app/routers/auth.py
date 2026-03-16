from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import hashlib
from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse, LoginRequest, TokenResponse
from ..auth import create_access_token, verify_admin

router = APIRouter()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user already exists
    result = await db.execute(select(User).where(User.phone == user_in.phone))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Пользователь с таким номером уже существует")
    
    db_user = User(
        phone=user_in.phone,
        password_hash=hash_password(user_in.password),
        full_name=user_in.full_name,
        email=user_in.email,
        telegram=user_in.telegram
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
    
    if not user or user.password_hash != hash_password(login_data.password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    access_token = create_access_token(data={"sub": str(user.id), "type": "user"})
    return {"access_token": access_token, "token_type": "bearer", "user_type": "user"}
