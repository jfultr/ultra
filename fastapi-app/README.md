## FastAPI App

Simple FastAPI backend with JWT auth and items CRUD.

### Run locally

1. Create venv and install deps:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -r <(python - <<'PY'
print("\n".join([
    "fastapi>=0.111.0",
    "uvicorn[standard]>=0.30.0",
    "SQLAlchemy>=2.0.25",
    "pydantic>=2.7.0",
    "pydantic-settings>=2.2.1",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "pytest>=8.0.0",
    "httpx>=0.27.0",
]))
PY
)
```

2. Copy env and run:

```bash
cp .env.example .env
uvicorn app.main:app --reload
```

API at `http://localhost:8000` and docs at `http://localhost:8000/docs`.

### Run tests

```bash
pytest -q
```

### Docker

```bash
docker build -t fastapi-app .
docker run -it --rm -p 8000:8000 --env-file .env fastapi-app
```


