"""Routes de gestion des tâches."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth
from app.routes.projects import get_project_or_404, ensure_project_access

router = APIRouter(tags=["tasks"])

VALID_STATUSES = {"todo", "in_progress", "done"}


def get_task_or_404(task_id: int, db: Session) -> models.Task:
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tâche introuvable"
        )
    return task


def ensure_assignee_is_allowed(project: models.Project, assignee_id: Optional[int], db: Session):
    """Une tâche ne peut être assignée qu'au propriétaire ou à un participant du projet."""
    if assignee_id is None:
        return
    user = db.query(models.User).filter(models.User.id == assignee_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Utilisateur assigné introuvable"
        )
    is_owner = project.owner_id == assignee_id
    is_participant = any(p.id == assignee_id for p in project.participants)
    if not (is_owner or is_participant):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La tâche ne peut être assignée qu'au propriétaire ou à un participant du projet",
        )


@router.post(
    "/projects/{project_id}/tasks",
    response_model=schemas.TaskOut,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    project_id: int,
    payload: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    project = get_project_or_404(project_id, db)
    ensure_project_access(project, current_user)

    status_value = payload.status or "todo"
    if status_value not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Statut invalide, valeurs autorisées : {sorted(VALID_STATUSES)}",
        )

    ensure_assignee_is_allowed(project, payload.assignee_id, db)

    task = models.Task(
        title=payload.title,
        description=payload.description,
        status=status_value,
        project_id=project.id,
        assignee_id=payload.assignee_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/projects/{project_id}/tasks", response_model=List[schemas.TaskOut])
def list_tasks(
    project_id: int,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    project = get_project_or_404(project_id, db)
    ensure_project_access(project, current_user)

    query = db.query(models.Task).filter(models.Task.project_id == project_id)
    if status_filter is not None:
        if status_filter not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Statut invalide, valeurs autorisées : {sorted(VALID_STATUSES)}",
            )
        query = query.filter(models.Task.status == status_filter)

    return query.all()


@router.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    task = get_task_or_404(task_id, db)
    project = get_project_or_404(task.project_id, db)
    ensure_project_access(project, current_user)
    return task


@router.put("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: int,
    payload: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    task = get_task_or_404(task_id, db)
    project = get_project_or_404(task.project_id, db)
    ensure_project_access(project, current_user)

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.status is not None:
        if payload.status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Statut invalide, valeurs autorisées : {sorted(VALID_STATUSES)}",
            )
        task.status = payload.status
    if payload.assignee_id is not None:
        ensure_assignee_is_allowed(project, payload.assignee_id, db)
        task.assignee_id = payload.assignee_id

    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    task = get_task_or_404(task_id, db)
    project = get_project_or_404(task.project_id, db)
    ensure_project_access(project, current_user)

    db.delete(task)
    db.commit()
    return None
