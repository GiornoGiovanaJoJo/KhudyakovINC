from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import TeamMember
from ..schemas import TeamMemberCreate, TeamMemberUpdate, TeamMemberResponse
from ..auth import get_current_admin

router = APIRouter()


@router.get("/", response_model=list[TeamMemberResponse])
async def get_team(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TeamMember).order_by(TeamMember.order))
    return result.scalars().all()


@router.post("/", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def create_member(
    data: TeamMemberCreate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    member = TeamMember(**data.model_dump())
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


@router.put("/{member_id}", response_model=TeamMemberResponse)
async def update_member(
    member_id: int,
    data: TeamMemberUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(TeamMember).where(TeamMember.id == member_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(member, key, value)

    await db.commit()
    await db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(TeamMember).where(TeamMember.id == member_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    await db.delete(member)
    await db.commit()
