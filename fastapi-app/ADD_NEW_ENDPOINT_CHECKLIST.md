### Checklist: Add a New Endpoint to this FastAPI App

This project uses FastAPI with JWT auth, SQLAlchemy models, a CRUD layer, and versioned routing under `settings.API_V1_STR` (currently `"/api"`). Follow this checklist when adding a new endpoint.

- **Core files**:
  - Routers: `app/api/routers/*.py` (mounted in `app/main.py`)
  - Auth/Deps: `app/api/deps.py`, `app/core/security.py`
  - Models/DB: `app/db/models.py`, `app/db/crud.py`, `app/db/session.py`, `app/db/base.py`
  - Schemas: `app/schemas/*.py`
  - Settings: `app/core/config.py`
  - Tests: `tests/`

### 0) Decide scope
- [ ] Path and method(s): under `settings.API_V1_STR` (e.g., `/api/<resource>`)
- [ ] Auth required? Use `Depends(get_current_user)` if protected
- [ ] Needs DB? New model/table or reuse existing? New CRUD needed?
- [ ] Response models and status codes

### 1) Define Pydantic schemas (if returning/accepting data)
- [ ] Create `app/schemas/<resource>.py` with `Create`, `Update`, `Out` models
- [ ] Reuse existing schema(s) where possible
- [ ] Ensure fields and optionality match your API contract

Example:
```python
# app/schemas/widget.py
from typing import Optional
from pydantic import BaseModel

class WidgetBase(BaseModel):
    name: str
    description: Optional[str] = None

class WidgetCreate(WidgetBase):
    pass

class WidgetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class WidgetOut(WidgetBase):
    id: int
    class Config:
        from_attributes = True
```

### 2) Add/Update SQLAlchemy models (only if new table/entity)
- [ ] Edit `app/db/models.py` to add the model and relationships
- [ ] For local/dev, tables are created at startup via `Base.metadata.create_all`
- [ ] For production, prefer Alembic migrations

Example:
```python
# app/db/models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Widget(Base):
    __tablename__ = "widgets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
```

### 3) CRUD functions (data-backed endpoints)
- [ ] Implement create/read/update/delete helpers in `app/db/crud.py`
- [ ] Return full model instances; commit and refresh when mutating

Example:
```python
# app/db/crud.py
from sqlalchemy.orm import Session
from app.db import models

def get_widgets(db: Session, owner_id: int):
    return db.query(models.Widget).filter(models.Widget.owner_id == owner_id).all()
```

### 4) Create a router
- [ ] Add `app/api/routers/<resource>.py`
- [ ] Use `APIRouter(prefix="/<resource>", tags=["<resource>"])`
- [ ] Inject `db: Session = Depends(get_db)` and auth via `current_user = Depends(get_current_user)` if protected
- [ ] Set `response_model` and `status_code`

Example (protected, DB-backed):
```python
# app/api/routers/widgets.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db import crud, models
from app.schemas.widget import WidgetCreate, WidgetUpdate, WidgetOut

router = APIRouter(prefix="/widgets", tags=["widgets"])

@router.get("/", response_model=List[WidgetOut])
def list_widgets(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_widgets(db, owner_id=current_user.id)
```

Example (simple, public utility):
```python
# app/api/routers/health.py
from fastapi import APIRouter
router = APIRouter(prefix="/health", tags=["health"]) 

@router.get("/ping")
def ping():
    return {"status": "ok"}
```

### 5) Mount the router
- [ ] In `app/main.py`, include the new router with the API prefix

```python
# app/main.py
from app.api.routers import auth, items, widgets  # add your module
application.include_router(widgets.router, prefix=settings.API_V1_STR)
```

### 6) Tests
- [ ] Add tests in `tests/` (see `tests/test_items.py` for patterns)
- [ ] Use `TestClient` and, if protected, obtain a token via signup/login helper
- [ ] Cover: create/list/get/update/delete and error cases (404/401)

```python
# tests/test_widgets.py
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_widgets_flow():
    res = client.post("/api/auth/signup", json={"email": "u@e.com", "password": "p"})
    if res.status_code != 409:
        assert res.status_code == 200, res.text
    res = client.post("/api/auth/login", data={"username": "u@e.com", "password": "p"})
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # ... your assertions ...
```

### 7) Run and validate
- [ ] Start the app: `uvicorn app.main:app --reload`
- [ ] Visit Swagger UI at `/docs` and try the endpoint
- [ ] Run tests: `pytest -q`

### 8) Security and correctness checks
- [ ] Proper status codes (`201` for create, `204` for delete)
- [ ] Use `HTTPException` with clear messages for 401/404/409
- [ ] Do not leak internal fields (use `response_model`)
- [ ] If protected, ensure `Authorization: Bearer <token>` is required

### 9) Optional: Alembic (production)
- [ ] Create migration and upgrade DB instead of relying on `create_all`

---

### Minimal Quick-Start (public utility endpoint)
1. Create `app/api/routers/health.py` with a `GET /health/ping` route
2. Mount it in `app/main.py` with `prefix=settings.API_V1_STR`
3. Run and verify at `/api/health/ping`

```python
# app/api/routers/health.py
from fastapi import APIRouter
router = APIRouter(prefix="/health", tags=["health"]) 
@router.get("/ping")
def ping():
    return {"status": "ok"}
```

```python
# app/main.py
from app.api.routers import auth, items, health
application.include_router(health.router, prefix=settings.API_V1_STR)
```

This mirrors the existing style in `app/api/routers/items.py` and integrates with the JWT/auth flow via `app/api/deps.py` when needed.

