import logging
from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)

SOURCE_DIR = Path(__file__).resolve().parent.parent.parent


class GunicornConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    timeout: int = 900


class LoggingConfig(BaseModel):
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "debug"
    log_format: str = LOG_DEFAULT_FORMAT

    @property
    def log_level_value(self) -> int:
        return logging.getLevelNamesMapping()[self.log_level.upper()]


class EnvironmentOption(str, Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentSettings(BaseModel):
    current: EnvironmentOption = EnvironmentOption.LOCAL


class AppSettings(BaseModel):
    environment: EnvironmentSettings = EnvironmentSettings()
    APP_NAME: str = "FastAPI app"
    APP_DESCRIPTION: str | None = None
    APP_VERSION: str | None = None
    LICENSE_NAME: str | None = ""
    CONTACT_NAME: str | None = None
    CONTACT_EMAIL: str | None = None


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    users: str = "/users"
    superuser: str = "/superadmin"
    posts: str = "/posts"
    tiers: str = "/tiers"
    rate_limits: str = "/rate-limits"
    roles: str = "/roles"
    persons: str = "/persons"
    departments: str = "/departments"


class ApiPrefix(BaseModel):
    prefix: str = "/api"

    v1: ApiV1Prefix = ApiV1Prefix()


class CryptSettings(BaseModel):
    PRIVATE_KEY: Path = SOURCE_DIR / "certs" / "jwt-private.pem"
    PUBLIC_KEY: Path = SOURCE_DIR / "certs" / "jwt-public.pem"
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    TOKEN_TYPE_FIELD: str = "type"
    ACCESS_TOKEN_TYPE: str = "access"
    REFRESH_TOKEN_TYPE: str = "refresh"
    REFRESH_TOKEN_HTTPONLY: bool = True
    REFRESH_TOKEN_COOKIE_SECURE: bool = True
    REFRESH_TOKEN_COOKIE_SAMESITE: str = "Lax"


class RedisClient(BaseModel):
    HOST: str = "localhost"
    PORT: int = 6379


class RedisCache(BaseModel):
    CACHE_EXPIRATION: int = 3600


class RateLimitConfig(BaseModel):
    DEFAULT_LIMIT: int = 10
    DEFAULT_PERIOD: int = 60


class ImageSettings(BaseModel):
    UPLOAD_PATH: str = "storage"
    BASE_URL: str = "https://example.com"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB


class FirstTierConfig(BaseModel):
    NAME: str = "free"


class SuperUserConfig(BaseModel):
    PHONE_NUMBER: str = "phone"
    EMAIL: str = "email"
    USERNAME: str = "username"
    PASSWORD: str = "strong_password"


class EskizSettings(BaseModel):
    FROM: str = "4546"
    EMAIL: str = "email@test.com"
    PASSWORD: str = "password"
    TEMPLATE_TEXT: str = "plain text"
    TEST_PHONE_NUMBER: str = "phone"


class DbConfig(BaseModel):
    sync_url: PostgresDsn
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10
    CREATE_TABLES_ON_START: bool
    DROP_TABLES_ON_START: bool

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix="APP__",
        env_nested_delimiter="__",
        env_file=(
            SOURCE_DIR / ".env.template",
            SOURCE_DIR / ".env.dev",
            SOURCE_DIR / ".env",
        ),
        extra="ignore",
    )
    gunicorn: GunicornConfig = GunicornConfig()
    app_settings: AppSettings = AppSettings()
    logging_config: LoggingConfig = LoggingConfig()
    api: ApiPrefix = ApiPrefix()
    db: DbConfig
    crypt: CryptSettings
    redis_client: RedisClient = RedisClient()
    redis_cache: RedisCache = RedisCache()
    rate_limit: RateLimitConfig = RateLimitConfig()
    upload_settings: ImageSettings = ImageSettings()
    first_tier: FirstTierConfig = FirstTierConfig()
    first_superuser: SuperUserConfig = SuperUserConfig()
    eskiz: EskizSettings = EskizSettings()


# noinspection PyArgumentList
settings = Settings()
print(SOURCE_DIR)
print(EnvironmentOption.LOCAL)
print(settings.app_settings.environment.current.value)
