## FastAPI App

Simple FastAPI backend with JWT auth and items CRUD.

### Run locally

1. Create conda env and install deps:

```bash
conda env create -f environment.yml
conda activate fastapi-app
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


