from sqlmodel import Session, create_engine, SQLModel
from typing import Generator


class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=True)
        SQLModel.metadata.create_all(self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        with Session(self.engine) as session:
            yield session


db_manager: DatabaseManager = None


def get_session():
    if not db_manager:
        raise Exception("Database manager not initialized")
    yield from db_manager.get_session()
