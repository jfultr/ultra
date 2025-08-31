from fastapi import FastAPI

from app.api.routers import auth, items
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


def create_app() -> FastAPI:
    application = FastAPI(title=settings.PROJECT_NAME, version="0.1.0", debug=settings.DEBUG)

    # Routers
    application.include_router(auth.router, prefix=settings.API_V1_STR)
    application.include_router(items.router, prefix=settings.API_V1_STR)

    @application.on_event("startup")
    def on_startup() -> None:
        # For demo/dev: create tables automatically. Prefer Alembic in production.
        Base.metadata.create_all(bind=engine)

    return application


app = create_app()


