from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import PortfolioProject
from ..schemas import PortfolioCreate, PortfolioUpdate, PortfolioResponse
from ..auth import get_current_admin

router = APIRouter()


@router.get("/", response_model=list[PortfolioResponse])
async def get_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PortfolioProject).order_by(PortfolioProject.order))
    return result.scalars().all()


@router.get("/{slug}", response_model=PortfolioResponse)
async def get_project_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PortfolioProject).where(PortfolioProject.slug == slug))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: PortfolioCreate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    project = PortfolioProject(**data.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.put("/{project_id}", response_model=PortfolioResponse)
async def update_project(
    project_id: int,
    data: PortfolioUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(PortfolioProject).where(PortfolioProject.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)

    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(PortfolioProject).where(PortfolioProject.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    await db.delete(project)
    await db.commit()
