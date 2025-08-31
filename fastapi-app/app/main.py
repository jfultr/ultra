from fastapi import FastAPI

from app.api.routers import auth, items
from app.db.base import Base
from app.db.session import engine


def create_app() -> FastAPI:
    application = FastAPI(title="FastAPI App", version="0.1.0")

    # Routers
    application.include_router(auth.router, prefix="/api")
    application.include_router(items.router, prefix="/api")

    @application.on_event("startup")
    def on_startup() -> None:
        # For demo/dev: create tables automatically. Prefer Alembic in production.
        Base.metadata.create_all(bind=engine)

    return application


app = create_app()


