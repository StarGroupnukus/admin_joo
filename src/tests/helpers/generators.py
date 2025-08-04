from typing import Optional

from sqlalchemy.orm import Session

from app.core.auth.utils import hash_password
from app.models import User
from tests.conftest import fake


def create_user(  # noqa: PLR0913
    db: Session,
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone_number: Optional[str] = None,
    password: Optional[str] = None,
    image_url: Optional[str] = None,
    is_super_user: bool = False,
) -> User:
    _name = name or fake.name()
    _email = email or fake.email()
    _phone = phone_number or fake.numerify(text="##########")
    _password = password or fake.password()
    _image_url = image_url or fake.image_url()

    _user = User(
        name=_name,
        email=_email,
        phone_number=_phone,
        hashed_password=hash_password(_password),
        image_url=_image_url,
        is_superuser=is_super_user,
    )
    db.add(_user)
    db.commit()
    db.refresh(_user)

    return _user
