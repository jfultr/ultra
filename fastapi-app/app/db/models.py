from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    project_memberships = relationship("ProjectMembership", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", secondary="project_memberships", back_populates="users", viewonly=True)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    memberships = relationship("ProjectMembership", back_populates="project", cascade="all, delete-orphan")
    users = relationship("User", secondary="project_memberships", back_populates="projects", viewonly=True)


class ProjectMembership(Base):
    __tablename__ = "project_memberships"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True, index=True)
    # roles: owner, editor, viewer
    role = Column(String(50), nullable=False, default="owner")

    user = relationship("User", back_populates="project_memberships")
    project = relationship("Project", back_populates="memberships")
    


