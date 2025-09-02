from fastapi import FastAPI

from app.api.routers import auth, projects, membership
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


from contextlib import asynccontextmanager
from fastapi import FastAPI


import os
import logging

# app logger
logger = logging.getLogger("fastapi")

handler = logging.FileHandler("fastapi.log")
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.setLevel(logging.INFO if os.getenv("ENV") == "production" else logging.DEBUG)
logger.propagate = False  # disables propagation upward (so root logger doesn't collect other logs)

logger.info("Starting app in " + os.getenv("ENV") + " mode")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup

    # 1: For demo/dev: create tables automatically. Prefer Alembic in production.
    if os.getenv("ENV") == "development":
        Base.metadata.create_all(bind=engine)

    # 2: Ensure first superuser is created
    ensure_first_superuser()

    # running app
    yield

    # shutdown
    pass


def ensure_first_superuser():
    from app.db.session import SessionLocal
    from sqlalchemy.orm import Session
    from app.db.crud import get_user_by_email, create_user

    db: Session = SessionLocal()

    if get_user_by_email(db, email):
        return

    # Создаём сессию вручную или используем get_db()
    try:
        email = os.getenv("SUPER_EMAIL")
        password = os.getenv("SUPER_PASS")

        if not (email and password):
            return  # пропускаем, если не задано (или логируем предупреждение)

        create_user(db, email=email, password=password, is_superuser=True)
    finally:
        db.close()


def create_app() -> FastAPI:
    application = FastAPI(title=settings.PROJECT_NAME, version="0.1.0", debug=settings.DEBUG)

    # Routers
    application.include_router(auth.router, prefix=settings.API_V1_STR)
    application.include_router(projects.router, prefix=settings.API_V1_STR)
    application.include_router(membership.router, prefix=settings.API_V1_STR)

    return application


app = create_app()


