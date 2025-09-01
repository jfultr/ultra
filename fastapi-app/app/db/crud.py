from typing import Iterable, Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.db import models


# Users
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, email: str, password: str, is_superuser: bool = False) -> models.User:
    user = models.User(email=email, hashed_password=get_password_hash(password), is_superuser=is_superuser)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# Projects
def get_projects(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> list[models.Project]:
    return (
        db.query(models.Project)
        .filter(models.Project.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_project(db: Session, owner_id: int, project_id: int) -> Optional[models.Project]:
    return db.query(models.Project).filter(models.Project.owner_id == owner_id, models.Project.id == project_id).first()


def create_project(db: Session, owner_id: int, title: str, description: Optional[str]) -> models.Project:
    project = models.Project(owner_id=owner_id, title=title, description=description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(
    db: Session,
    owner_id: int,
    project_id: int,
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[models.Project]:
    project = get_project(db, owner_id=owner_id, project_id=project_id)
    if project is None:
        return None
    if title is not None:
        project.title = title
    if description is not None:
        project.description = description
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, owner_id: int, project_id: int) -> bool:
    project = get_project(db, owner_id=owner_id, project_id=project_id)
    if project is None:
        return False
    db.delete(project)
    db.commit()
    return True



