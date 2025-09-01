from pydantic import BaseModel, EmailStr
from typing import Literal


class MembershipIn(BaseModel):
    principal: EmailStr
    role: Literal["owner", "editor", "viewer"] = "viewer"


class MembershipUpdate(BaseModel):
    role: Literal["owner", "editor", "viewer"]


class MembershipOut(BaseModel):
    user_id: int
    project_id: int
    role: Literal["owner", "editor", "viewer"]

    class Config:
        from_attributes = True


