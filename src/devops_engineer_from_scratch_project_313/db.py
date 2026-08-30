from collections.abc import Generator
from functools import lru_cache

from sqlmodel import Session, SQLModel, create_engine


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)

    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return database_url


@lru_cache
def get_engine(database_url: str):
    normalized_url = normalize_database_url(database_url)
    connect_args = (
        {"check_same_thread": False}
        if normalized_url.startswith("sqlite")
        else {}
    )
    return create_engine(normalized_url, connect_args=connect_args)


def create_db_and_tables(database_url: str) -> None:
    engine = get_engine(database_url)
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    from devops_engineer_from_scratch_project_313.settings import get_settings

    engine = get_engine(get_settings().database_url)
    with Session(engine) as session:
        yield session
