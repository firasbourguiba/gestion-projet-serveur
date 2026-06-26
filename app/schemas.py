"""Schémas Pydantic utilisés pour valider les entrées et formater les sorties de l'API."""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Auth / User ----------

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Project ----------

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    owner: UserOut
    participants: List[UserOut] = []


class ProjectListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    owner_id: int


# ---------- Task ----------

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "todo"
    assignee_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assignee_id: Optional[int] = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    status: str
    project_id: int
    assignee_id: Optional[int] = None


# ---------- Participants ----------

class ParticipantAdd(BaseModel):
    email: EmailStr
