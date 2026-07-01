"""Routes de gestion des participants d'un projet."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth
from app.routes.projects import get_project_or_404, ensure_project_access

router = APIRouter(prefix="/projects/{project_id}/participants", tags=["participants"])


def ensure_owner(project: models.Project, user: models.User):
    if project.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le proprietaire peut gerer les participants",
        )


@router.post("", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def add_participant(
    project_id: int,
    payload: schemas.ParticipantAdd,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    project = get_project_or_404(project_id, db)
    ensure_owner(project, current_user)

    user_to_add = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user_to_add:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun utilisateur trouve avec cet email",
        )

    if user_to_add.id == project.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le proprietaire est deja associe au projet",
        )

    if any(p.id == user_to_add.id for p in project.participants):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet utilisateur est deja participant du projet",
        )

    project.participants.append(user_to_add)
    db.commit()
    return user_to_add


@router.get("", response_model=List[schemas.UserOut])
def list_participants(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    project = get_project_or_404(project_id, db)
    ensure_project_access(project, current_user)
    return project.participants


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_participant(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    project = get_project_or_404(project_id, db)
    ensure_owner(project, current_user)

    participant = next((p for p in project.participants if p.id == user_id), None)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cet utilisateur ne fait pas partie des participants",
        )

    project.participants.remove(participant)
    db.commit()
    return None
