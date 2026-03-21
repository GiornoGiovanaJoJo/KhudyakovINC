from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from ..database import get_db
from ..models import DeviceToken
from ..auth import get_current_admin

router = APIRouter()


class PushTokenRequest(BaseModel):
    token: str
    platform: str = "android"


@router.post("/register")
async def register_push_token(
    data: PushTokenRequest,
    db: AsyncSession = Depends(get_db),
    admin_username: str = Depends(get_current_admin),
):
    """Register a device push token for the authenticated admin."""
    # Check if token already exists
    result = await db.execute(
        select(DeviceToken).where(DeviceToken.token == data.token)
    )
    existing = result.scalars().first()

    if existing:
        existing.admin_username = admin_username
        existing.platform = data.platform
    else:
        db_token = DeviceToken(
            token=data.token,
            platform=data.platform,
            admin_username=admin_username,
        )
        db.add(db_token)

    await db.commit()
    return {"status": "ok", "message": "Token registered"}


@router.post("/test")
async def test_push(
    db: AsyncSession = Depends(get_db),
    admin_username: str = Depends(get_current_admin),
):
    """Test endpoint — returns all registered tokens for debugging."""
    result = await db.execute(select(DeviceToken))
    tokens = result.scalars().all()
    return {
        "count": len(tokens),
        "tokens": [
            {"id": t.id, "platform": t.platform, "admin": t.admin_username}
            for t in tokens
        ],
    }
