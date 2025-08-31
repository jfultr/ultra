from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db import crud, models
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate


router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=List[ItemOut])
def list_items(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_items(db, owner_id=current_user.id)


@router.post("/", response_model=ItemOut, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_item(db, owner_id=current_user.id, title=payload.title, description=payload.description)


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    item = crud.get_item(db, owner_id=current_user.id, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=ItemOut)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    item = crud.update_item(db, owner_id=current_user.id, item_id=item_id, title=payload.title, description=payload.description)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ok = crud.delete_item(db, owner_id=current_user.id, item_id=item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Item not found")
    return None


