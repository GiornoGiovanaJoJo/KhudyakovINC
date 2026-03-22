import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.hash import bcrypt
import hashlib

from ..database import get_db
from ..models import Lead, User, UserRole
from ..schemas import LeadResponse, UserResponse, UserUpdate, UserCreate
from ..deps import get_current_active_user, require_role

logger = logging.getLogger(__name__)

router = APIRouter()

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hash(password)

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    if isinstance(current_user, dict):
        raise HTTPException(status_code=400, detail="Cannot get user profile for superadmin")
    return current_user

@router.get("/my-leads", response_model=list[LeadResponse])
async def get_my_leads(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    if isinstance(current_user, dict):
        # Superadmin sees all leads or none here, but normally they use /api/leads
        result = await db.execute(select(Lead).order_by(Lead.created_at.desc()))
        return result.scalars().all()
    user_id = current_user.id
    result = await db.execute(select(Lead).where(Lead.user_id == user_id).order_by(Lead.created_at.desc()))
    return result.scalars().all()

@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    if isinstance(current_user, dict):
        raise HTTPException(status_code=400, detail="Cannot update superadmin profile this way")
    
    db_user = current_user
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        db_user.password_hash = hash_password(update_data["password"])
        del update_data["password"]
    
    # Don't let users change their own role unless they are admin
    if "role" in update_data and current_user.role != UserRole.ADMIN:
        del update_data["role"]
        
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user

# ── Admin User Management ────────────────────────────────────

@router.get("/", response_model=list[UserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()

@router.post("/", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_role([UserRole.ADMIN]))
):
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

@router.patch("/{user_id}", response_model=UserResponse)
async def update_any_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_role([UserRole.ADMIN]))
):
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
        
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        db_user.password_hash = hash_password(update_data["password"])
        del update_data["password"]
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_role([UserRole.ADMIN]))
):
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    await db.delete(db_user)
    await db.commit()
    return {"status": "ok"}
