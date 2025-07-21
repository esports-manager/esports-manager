#      eSports Manager - A free and open source eSports management simulation game
#      Copyright (C) 2020-2025  Pedrenrique G. Guimarães
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
