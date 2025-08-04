from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_auth_user as get_current_user
from app.core.auth.validation import http_bearer

from .conftest import fake, override_dependency
from .helpers import generators, mocks


def test_get_user(
    db: Session,
    client: TestClient,
) -> None:
    user = generators.create_user(
        db,
    )

    response = client.get(f"/api/v1/superadmin/users/{user.id}")
    assert response.status_code == status.HTTP_200_OK

    response = response.json()
    data = response["data"]
    assert data["name"] == user.name


def test_get_users(
    db: Session,
    client: TestClient,
) -> None:
    count = 5
    for _ in range(count):
        generators.create_user(db)

    response = client.get("/api/v1/superadmin/users/list")
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    pagination = response["pagination"]
    assert pagination["total"] >= count


def test_delete_user(
    db: Session,
    client: TestClient,
    mocker: MockerFixture,
) -> None:
    user = generators.create_user(db)

    # mock_user_func = lambda: user_read
    override_dependency(
        get_current_user,
        mocks.get_current_user(user),
    )
    override_dependency(
        http_bearer,
        mocks.oauth2_scheme(),
    )

    mocker.patch(
        "app.core.auth.utils.decode_jwt",
        return_value={
            "sub": user.name,
            "exp": 999,
        },
    )

    response = client.delete("/api/v1/users/me")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_update_me(
    db: Session,
    client: TestClient,
) -> None:
    user = generators.create_user(db)
    new_name = fake.name()

    override_dependency(
        get_current_user,
        mocks.get_current_user(user),
    )

    response = client.put(
        "/api/v1/users/me",
        json={
            "name": new_name,
        },
    )
    assert response.status_code == status.HTTP_200_OK
