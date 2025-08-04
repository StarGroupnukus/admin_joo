import logging
import secrets
import string
from datetime import datetime
from enum import Enum
from typing import Optional

import httpx
from fastapi import status
from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings

logger = logging.getLogger(__name__)
RETRIES = 3
CODE_LENGTH = 5


# region Models
class Network(str, Enum):
    MAIN = "https://notify.eskiz.uz"

    def __str__(self):
        return self.value


class TokenExpired(Exception):
    pass


class AuthenticationError(Exception):
    pass


class TokenData(BaseModel):
    token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    message: str
    data: TokenData
    token_type: str


class RefreshTokenResponse(BaseModel):
    pass


class UserData(BaseModel):
    id: int
    name: str
    email: str
    password: str
    role: str
    status: str
    is_vip: bool
    balance: int
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseModel):
    status: str
    data: UserData
    id: int | None = None


class SendSMSRequest(BaseModel):
    phone_number: str = Field(pattern=r"^[1-9]\d{1,14}$")
    message: str
    from_: str
    callback_url: str

    def to_form_data(self):
        return {
            "mobile_phone": self.phone_number,
            "message": self.message,
            "from": self.from_,
            "callback_url": self.callback_url,
        }


class SendSMSResponse(BaseModel):
    id: str
    message: str
    status: str


# endregion
# region HttpClient
class AsyncHttpClient:
    @staticmethod
    async def request(
        method: str,
        url: str,
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
        timeout: int = 60,
    ):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method, url=url, headers=headers, data=data, timeout=timeout
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                logger.error(
                    f"HTTP error {exc.response.status_code}: {exc.response.text}"
                )
                if exc.response.status_code == status.HTTP_401_UNAUTHORIZEDs:
                    if "auth/login" in url:
                        raise AuthenticationError("Invalid credentials") from exc
                    raise TokenExpired() from exc
                raise


# endregion
# region EskizClient
class AsyncEskizClient:
    def __init__(
        self,
        email: str,
        password: str,
        network: Network = Network.MAIN,
        from_: str = settings.eskiz.FROM,
        callback: str = "",
    ):
        self.email = email
        self.password = password
        self.network = network
        self.from_ = from_
        self.callback = callback
        self.token = None
        self.headers = {}

    async def login(self):
        url = f"{self.network}/api/auth/login"
        payload = LoginRequest(
            email=self.email,
            password=self.password,
        ).model_dump()

        response = await AsyncHttpClient.request(
            "POST",
            url,
            data=payload,
        )
        login_data = LoginResponse(**response)
        self.token = login_data.data.token
        self.headers["Authorization"] = f"Bearer {self.token}"
        return login_data

    async def refresh_token(self):
        url = f"{self.network}/api/auth/refresh"
        response = await AsyncHttpClient.request(
            "PATCH",
            url,
            headers=self.headers,
        )
        refresh_data = RefreshTokenResponse(**response)
        self.token = refresh_data.data.token
        self.headers["Authorization"] = f"Bearer {self.token}"
        return refresh_data

    async def get_user(self):
        url = f"{self.network}/api/auth/user"
        try:
            response = await AsyncHttpClient.request(
                "GET",
                url,
                headers=self.headers,
            )
            return UserResponse(**response)
        except TokenExpired:
            await self.login()
            return await self.get_user()

    async def send_sms(
        self,
        phone_number: str,
        message: str,
        retries: int = RETRIES,
    ) -> SendSMSResponse:
        url = f"{self.network}/api/message/sms/send"
        data = SendSMSRequest(
            phone_number=phone_number,
            message=message,
            from_=self.from_,
            callback_url=self.callback,
        ).to_form_data()

        for attempt in range(retries):
            try:
                response = await AsyncHttpClient.request(
                    "POST",
                    url,
                    headers=self.headers,
                    data=data,
                )
                return SendSMSResponse(**response)
            except TokenExpired:
                if attempt < retries:
                    await self.login()
                    continue
                raise


# endregion
def code_generator(
    length: int = CODE_LENGTH,
) -> str:
    digits = string.digits
    return "".join(secrets.choice(digits) for _ in range(length))
