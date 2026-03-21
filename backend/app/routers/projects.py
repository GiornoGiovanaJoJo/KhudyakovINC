from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Project, UserRole
from ..schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from ..deps import get_current_active_user, require_role

router = APIRouter()

@router.get("/", response_model=list[ProjectResponse])
async def get_projects(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    query = select(Project).options(selectinload(Project.members))
    
    if isinstance(current_user, dict):
        pass # Superadmin sees all
    elif current_user.role in [UserRole.ADMIN, UserRole.MANAGER]:
        pass # Manager/Admin sees all
    else:
        # Employees only see projects where they are members
        query = query.where(Project.members.any(id=current_user.id))
        
    result = await db.execute(query.order_by(Project.created_at.desc()))
    return result.scalars().all()

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    manager_user = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    creator_id = None if isinstance(manager_user, dict) else manager_user.id
    
    db_project = Project(
        title=project_in.title,
        description=project_in.description,
        status=project_in.status,
        deadline=project_in.deadline,
        created_by_id=creator_id
    )
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    
    # Reload with members relationship so response model is fully populated
    result = await db.scalar(select(Project).options(selectinload(Project.members)).where(Project.id == db_project.id))
    return result

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    db_project = await db.scalar(
        select(Project).options(selectinload(Project.members)).where(Project.id == project_id)
    )
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if not isinstance(current_user, dict) and current_user.role == UserRole.EMPLOYEE:
        member_ids = [m.id for m in db_project.members]
        if current_user.id not in member_ids:
            raise HTTPException(status_code=403, detail="Access denied")
            
    return db_project

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    manager_user = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    db_project = await db.scalar(select(Project).options(selectinload(Project.members)).where(Project.id == project_id))
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
        
    await db.commit()
    await db.refresh(db_project)
    return db_project

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    manager_user = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    db_project = await db.get(Project, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(db_project)
    await db.commit()
    return {"status": "ok"}
