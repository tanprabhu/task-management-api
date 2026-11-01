from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app import models
from app.database import Base, get_db
from app.main import app


class TestSettings(BaseSettings):
    test_database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


test_settings = TestSettings()
test_database_url = make_url(test_settings.test_database_url)

if not test_database_url.database.endswith("_test"):
    raise RuntimeError(
        "Tests must use a database whose name ends with '_test'."
    )

test_engine = create_engine(
    test_settings.test_database_url,
    pool_pre_ping=True,
)


@pytest.fixture(scope="session", autouse=True)
def test_schema() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    def override_get_db() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_db, None)
    session.close()
    transaction.rollback()
    connection.close()