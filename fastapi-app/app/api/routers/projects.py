from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db import crud, models
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.schemas.membership import MembershipOut, MembershipUpdate, MembershipIn


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_projects(db, current_user_id=current_user.id)


@router.post("/", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_project(db, current_user_id=current_user.id, title=payload.title, description=payload.description)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    project = crud.get_project(db, current_user_id=current_user.id, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    project = crud.update_project(db, current_user_id=current_user.id, project_id=project_id, title=payload.title, description=payload.description)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ok = crud.delete_project(db, current_user_id=current_user.id, project_id=project_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Project not found")
    return None


# Membership endpoints
@router.get("/{project_id}/users", response_model=list[MembershipOut])
def list_project_members(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    memberships = crud.list_memberships(db, current_user_id=current_user.id, project_id=project_id)
    if not memberships:
        # Member-only access, otherwise 404 to avoid leaking existence
        raise HTTPException(status_code=404, detail="Project not found")
    return memberships


@router.post("/{project_id}/users", response_model=ProjectOut)
def add_member(project_id: int, payload: MembershipIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    
    # we got the email and role from the payload
    added_user_email = payload.principal
    added_user_role = payload.role

    # 1: find user id
    user = crud.get_user_by_email(db, email=added_user_email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user.id

    # 2: add user to project with viewer role
    project = crud.add_user_to_project(db, current_user_id=current_user.id, project_id=project_id, user_id=user_id)
    if project is None:
        # Either no permission or project not found from perspective of current user
        raise HTTPException(status_code=403, detail="Not allowed")

    # 3: update role if needed
    if added_user_role != "viewer":
        membership = crud.update_user_role(db, current_user_id=current_user.id, project_id=project_id, user_id=user_id, role=added_user_role)
        if membership is None:
            raise HTTPException(status_code=403, detail="Not allowed")

    return project


@router.put("/{project_id}/users", response_model=MembershipOut)
def update_member_role(project_id: int, payload: MembershipIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # we got the email and role from the payload
    updated_user_email = payload.principal
    updated_user_role = payload.role

    # 1: find user id
    user = crud.get_user_by_email(db, email=updated_user_email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user.id

    # 2: update role if needed
    membership = crud.update_user_role(db, current_user_id=current_user.id, project_id=project_id, user_id=user_id, role=updated_user_role)
    if membership is None:
        raise HTTPException(status_code=403, detail="Not allowed")

    return membership


@router.delete("/{project_id}/users", status_code=204)
def remove_member(project_id: int, payload: MembershipIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # we got the email from the payload
    removed_user_email = payload.principal

    # 1: find user id
    user = crud.get_user_by_email(db, email=removed_user_email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user.id

    # 2: remove user from project
    ok = crud.remove_user_from_project(db, current_user_id=current_user.id, project_id=project_id, user_id=user_id)
    if not ok:
        raise HTTPException(status_code=403, detail="Not allowed")
        
    return None

