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
def get_projects(db: Session, current_user_id: int, skip: int = 0, limit: int = 100) -> list[models.Project]:
    return (
        db.query(models.Project)
        .join(models.Project.memberships)
        .filter(models.ProjectMembership.user_id == current_user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_project(db: Session, current_user_id: int, project_id: int) -> Optional[models.Project]:
    return (
        db.query(models.Project)
        .join(models.Project.memberships)
        .filter(models.ProjectMembership.user_id == current_user_id, models.Project.id == project_id)
        .first()
    )


def create_project(db: Session, current_user_id: int, title: str, description: Optional[str]) -> models.Project:
    project = models.Project(title=title, description=description)
    db.add(project)
    # add owner membership
    membership = models.ProjectMembership(user_id=current_user_id, project=project, role="owner")
    db.add(membership)
    db.commit()
    db.refresh(project)
    return project


def update_project(
    db: Session,
    current_user_id: int,
    project_id: int,
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[models.Project]:
    project = get_project(db, current_user_id=current_user_id, project_id=project_id)
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


def delete_project(db: Session, current_user_id: int, project_id: int) -> bool:
    # Require owner role to delete the project
    owner_membership = (
        db.query(models.ProjectMembership)
        .filter(
            models.ProjectMembership.user_id == current_user_id,
            models.ProjectMembership.project_id == project_id,
            models.ProjectMembership.role == "owner",
        )
        .first()
    )
    if owner_membership is None:
        return False
    project = (
        db.query(models.Project)
        .filter(models.Project.id == project_id)
        .first()
    )
    if project is None:
        return False
    db.delete(project)
    db.commit()
    return True


def add_user_to_project(db: Session, current_user_id: int, project_id: int, user_id: int) -> Optional[models.Project]:
    # Only allow if current_user_id is a member with owner role
    membership = (
        db.query(models.ProjectMembership)
        .filter(
            models.ProjectMembership.user_id == current_user_id,
            models.ProjectMembership.project_id == project_id,
            models.ProjectMembership.role.in_(["owner"]),
        )
        .first()
    )
    if membership is None:
        return None
    existing = (
        db.query(models.ProjectMembership)
        .filter(models.ProjectMembership.user_id == user_id, models.ProjectMembership.project_id == project_id)
        .first()
    )
    if existing is None:
        db.add(models.ProjectMembership(user_id=user_id, project_id=project_id, role="viewer"))
        db.commit()
    return get_project(db, current_user_id=current_user_id, project_id=project_id)


def update_user_role(db: Session, current_user_id: int, project_id: int, user_id: int, role: str) -> Optional[models.ProjectMembership]:
    # Only owners can update roles
    owner_membership = (
        db.query(models.ProjectMembership)
        .filter(
            models.ProjectMembership.user_id == current_user_id,
            models.ProjectMembership.project_id == project_id,
            models.ProjectMembership.role == "owner",
        )
        .first()
    )
    if owner_membership is None:
        return None
    membership = (
        db.query(models.ProjectMembership)
        .filter(models.ProjectMembership.user_id == user_id, models.ProjectMembership.project_id == project_id)
        .first()
    )
    if membership is None:
        return None
    membership.role = role
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership



