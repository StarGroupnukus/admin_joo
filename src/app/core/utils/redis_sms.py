import json
import logging
from datetime import UTC, datetime, timedelta

from app.app_lifespan import redis_client

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 10
BLOCK_DURATION = 3600  # 1 час
SMS_EXPIRE_TIME = 120  # 2 минуты
VERIFIED_EXPIRE_TIME = 3600  # 1 час
BLOCKED_KEY_PREFIX = "blocked:"
SMS_KEY_PREFIX = "sms_code:"
REQUEST_COUNTER_PREFIX = "request_counter:"


def _get_sms_key(phone: str) -> str:
    return f"{SMS_KEY_PREFIX}{phone}"


def _get_blocked_key(phone: str) -> str:
    return f"{BLOCKED_KEY_PREFIX}{phone}"


async def block_phone(phone: str) -> None:
    """Блокирует номер на час"""
    logger.info(f"Blocking phone {phone}")
    # Устанавливаем блокировку
    await redis_client.client.set(_get_blocked_key(phone), "1", ex=BLOCK_DURATION)
    # Очищаем все данные
    await redis_client.client.delete(f"{REQUEST_COUNTER_PREFIX}{phone}")
    await redis_client.client.delete(_get_sms_key(phone))


async def is_blocked(phone: str) -> bool:
    blocked = await redis_client.client.get(_get_blocked_key(phone))
    logger.info(f"Checking block for {phone}: {blocked}")
    return bool(blocked)


async def get_sms_code_data(phone: str) -> dict | None:
    data = await redis_client.client.get(_get_sms_key(phone))
    if not data:
        return None
    return json.loads(data)


async def save_sms_code(phone: str, code: str) -> tuple[bool, str]:
    try:
        logger.info(f"Attempting to save code for {phone}")

        # Проверяем блокировку
        if await is_blocked(phone):
            logger.info(f"Phone {phone} is blocked")
            return False, "Phone number is blocked. Try again in an hour"

        # Получаем счетчик запросов кода
        request_counter = await redis_client.client.incr(
            f"{REQUEST_COUNTER_PREFIX}{phone}"
        )
        logger.info(f"Request counter for {phone}: {request_counter}")

        # Если это первый запрос, устанавливаем TTL
        if request_counter == 1:
            await redis_client.client.expire(
                f"{REQUEST_COUNTER_PREFIX}{phone}", BLOCK_DURATION
            )

        # Проверяем количество запросов
        if request_counter > MAX_ATTEMPTS:
            logger.info(
                f"Max attempts reached ({request_counter}), blocking {phone}",
            )
            await block_phone(phone)
            return False, "Too many attempts. Try again in an hour"

        # Создаем новые данные
        data = {
            "code": code,
            "created_at": datetime.now(UTC).isoformat(),
            "expires_at": (
                datetime.now(UTC) + timedelta(seconds=SMS_EXPIRE_TIME)
            ).isoformat(),
        }

        # Сохраняем в Redis
        await redis_client.client.set(
            _get_sms_key(phone), json.dumps(data), ex=SMS_EXPIRE_TIME
        )

        logger.info(
            f"Successfully saved code for {phone}. Attempt {request_counter} of {MAX_ATTEMPTS}"
        )
        return True, "SMS code saved successfully"

    except Exception as e:
        logger.error(f"Error in save_sms_code: {e!s}")
        return False, "Error saving SMS code"


async def verify_sms_code(phone: str, code: str) -> tuple[bool, str]:
    try:
        logger.info(f"Verifying code for {phone}")

        if await is_blocked(phone):
            return False, "Phone number is blocked. Try again in an hour"

        data = await get_sms_code_data(phone)
        if not data:
            return False, "Code not found"

        # Увеличиваем счетчик попыток
        data["attempts"] = data.get("attempts", 0) + 1
        logger.info(f"Attempts after increment: {data['attempts']}")

        # Проверяем количество попыток
        if data["attempts"] >= MAX_ATTEMPTS:
            logger.info(f"Max attempts reached in verify, blocking {phone}")
            await block_phone(phone)
            await delete_sms_code(phone)
            return False, "Too many attempts. Try again in an hour"

        # Сохраняем обновленные данные
        await redis_client.client.set(
            _get_sms_key(phone), json.dumps(data), ex=SMS_EXPIRE_TIME
        )

        if data["code"] != code:
            return False, "Invalid code"

        # Успешная верификация
        await delete_sms_code(phone)
        return True, "Success"

    except Exception as e:
        logger.error(f"Error in verify_sms_code: {e!s}")
        return False, f"Error verifying SMS code: {e!s}"


async def delete_sms_code(phone: str) -> None:
    """Удалить код"""
    await redis_client.client.delete(_get_sms_key(phone))
