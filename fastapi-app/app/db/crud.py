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


# Items
def get_items(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> list[models.Item]:
    return (
        db.query(models.Item)
        .filter(models.Item.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_item(db: Session, owner_id: int, item_id: int) -> Optional[models.Item]:
    return db.query(models.Item).filter(models.Item.owner_id == owner_id, models.Item.id == item_id).first()


def create_item(db: Session, owner_id: int, title: str, description: Optional[str]) -> models.Item:
    item = models.Item(owner_id=owner_id, title=title, description=description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(
    db: Session,
    owner_id: int,
    item_id: int,
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[models.Item]:
    item = get_item(db, owner_id=owner_id, item_id=item_id)
    if item is None:
        return None
    if title is not None:
        item.title = title
    if description is not None:
        item.description = description
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, owner_id: int, item_id: int) -> bool:
    item = get_item(db, owner_id=owner_id, item_id=item_id)
    if item is None:
        return False
    db.delete(item)
    db.commit()
    return True


