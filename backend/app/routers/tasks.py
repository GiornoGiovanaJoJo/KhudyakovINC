from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Task, UserRole, Project
from ..schemas import TaskCreate, TaskResponse, TaskUpdate
from ..deps import get_current_active_user, require_role

router = APIRouter()

@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    project_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    query = select(Task)
    
    if project_id:
        query = query.where(Task.project_id == project_id)
        
    if isinstance(current_user, dict):
        pass # superadmin sees all
    elif current_user.role in [UserRole.ADMIN, UserRole.MANAGER]:
        pass
    else:
        # employee only sees tasks assigned to them
        query = query.where(Task.assignee_id == current_user.id)
        
    result = await db.execute(query.order_by(Task.created_at.desc()))
    return result.scalars().all()

@router.post("/", response_model=TaskResponse)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
    manager_user = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    db_project = await db.get(Project, task_in.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    reporter_id = None if isinstance(manager_user, dict) else manager_user.id
    
    db_task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        project_id=task_in.project_id,
        assignee_id=task_in.assignee_id,
        reporter_id=reporter_id
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    db_task = await db.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    is_superadmin = isinstance(current_user, dict)
    
    if not is_superadmin and current_user.role == UserRole.EMPLOYEE:
        if db_task.assignee_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cannot edit tasks assigned to others")
            
        allowed_updates = {"status"}
        update_data = task_update.model_dump(exclude_unset=True)
        for k in update_data.keys():
            if k not in allowed_updates:
                raise HTTPException(status_code=403, detail=f"Employees cannot edit field: {k}")
    else:
        update_data = task_update.model_dump(exclude_unset=True)
        
    for key, value in update_data.items():
        setattr(db_task, key, value)
        
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    manager_user = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    db_task = await db.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(db_task)
    await db.commit()
    return {"status": "ok"}
