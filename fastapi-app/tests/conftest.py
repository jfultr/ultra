import os
import sys
import pytest


# Ensure project root is on sys.path so `import app` works when running from tests/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Force a local SQLite database for tests to avoid picking up external DSNs
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./test.db"

# Ensure the API prefix used by the app matches the tests
os.environ.setdefault("API_V1_STR", "/api")

# Hint the app it's running in tests
os.environ.setdefault("ENV", "test")
os.environ.setdefault("DEBUG", "True")


@pytest.fixture(scope="session", autouse=True)
def _create_test_db():
    # Import after env vars are set so settings picks them up
    from app.db.base import Base  # noqa: WPS433
    from app.db.session import engine  # noqa: WPS433

    Base.metadata.create_all(bind=engine)
    yield
    # Optional cleanup
    # Base.metadata.drop_all(bind=engine)


from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client() -> TestClient:
    client = TestClient(app)
    yield client
    client.close()


def signup_and_login(client: TestClient, email: str, password: str) -> str:
    res = client.post("/api/auth/signup", json={"email": email, "password": password})
    if not res.status_code == 409: 
        assert res.status_code == 200, res.text

    res = client.post("/api/auth/login", data={"username": email, "password": password})
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    return token