from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import Lead, User
from ..schemas import LeadResponse, UserResponse, UserUpdate
from ..auth import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = int(current_user["id"])
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/my-leads", response_model=list[LeadResponse])
async def get_my_leads(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = int(current_user["id"])
    result = await db.execute(
        select(Lead).where(Lead.user_id == user_id).order_by(Lead.created_at.desc())
    )
    return result.scalars().all()

@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = int(current_user["id"])
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        import hashlib
        db_user.password_hash = hashlib.sha256(update_data["password"].encode("utf-8")).hexdigest()
        del update_data["password"]
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user
