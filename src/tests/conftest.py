from typing import Any, Callable, Generator

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from app.core.config import settings
from app.main import main_app

DATABASE_URL = settings.db.sync_url
sync_engine = create_engine(str(DATABASE_URL))
local_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

fake = Faker()


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, Any, None]:
    with TestClient(main_app) as _client:
        yield _client
    main_app.dependency_overrides = {}
    sync_engine.dispose()


@pytest.fixture
def db() -> Generator[Session, Any, None]:
    session = local_session()
    yield session
    session.close()


def override_dependency(
    dependency: Callable[..., Any],
    mocked_response: Any,
) -> None:
    main_app.dependency_overrides[dependency] = lambda: mocked_response
