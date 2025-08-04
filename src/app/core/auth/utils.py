import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import bcrypt
import jwt

from app.core.config import settings

# from app.core.utils.eskiz_client import code_generator


def encode_jwt(
    payload: dict,
    private_key: Path = settings.crypt.PRIVATE_KEY.read_text(),
    algorithm: str = settings.crypt.ALGORITHM,
    expire_minutes: int = settings.crypt.ACCESS_TOKEN_EXPIRE_MINUTES,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(UTC)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)

    to_encode.update(
        exp=expire,
        iat=now,
        jti=str(uuid.uuid4()),
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: Path = settings.crypt.PUBLIC_KEY.read_text(),
    algorithm: str = settings.crypt.ALGORITHM,
) -> dict:
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=algorithm,
    )
    return decoded


def hash_password(
    password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


async def verify_password(
    password: str,
    hashed_password: str | bytes,
) -> bool:
    pwd_bytes: bytes = password.encode()
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode()
    return bcrypt.checkpw(
        password=pwd_bytes,
        hashed_password=hashed_password,
    )
