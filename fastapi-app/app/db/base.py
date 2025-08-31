from sqlalchemy.orm import declarative_base


Base = declarative_base()

# Import models to ensure they are registered with Base.metadata before create_all
# This import has side effects and is intentionally unused here.
from app.db import models as _models  # noqa: F401


