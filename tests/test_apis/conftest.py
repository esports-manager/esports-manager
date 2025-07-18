from typing import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
import pytest
from esm import create_api, get_session


@pytest.fixture
def session_fixture() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite:///memory", connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client_fixture(session_fixture: Session) -> TestClient:
    app = create_api(lifespan=None)

    def overide_get_session():
        yield session_fixture

    app.dependency_overrides[get_session] = overide_get_session
    with TestClient(app) as client:
        yield client
        app.dependency_overrides.clear()
