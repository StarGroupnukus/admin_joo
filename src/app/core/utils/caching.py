import functools
import json
import re
from collections.abc import Callable
from typing import Any

from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder

from app.app_lifespan import redis_client
from app.core.config import settings
from app.core.exceptions.cache_exceptions import (
    CacheIdentificationInferenceError,
    InvalidRequestError,
    MissingClientError,
)

# pool: ConnectionPool | None = None
# client: Redis | None = None


def _infer_resource_id(
    kwargs: dict[str, Any], resource_id_type: type | tuple[type, ...]
) -> int | str:
    """Определяет ID ресурса из словаря ключевых аргументов.

    Параметры
    ---------
    kwargs: Dict[str, Any]
        Словарь ключевых аргументов.
    resource_id_type: Union[type, Tuple[type, ...]]
        Ожидаемый тип ID ресурса, может быть целым числом (int) или строкой (str).

    Возвращает
    ----------
    Union[None, int, str]
        Определенный ID ресурса. Если не удается определить или не соответствует ожидаемому типу, возвращает None.

    Примечание
    ----------
        - Когда `resource_id_type` равен `int`, функция ищет аргумент с ключом 'id'.
        - Когда `resource_id_type` равен `str`, пытается определить ID ресурса как строку.
    """
    resource_id: int | str | None = None
    for arg_name, arg_value in kwargs.items():
        if isinstance(arg_value, resource_id_type):
            if (resource_id_type is int) and ("id" in arg_name):
                resource_id = arg_value

            elif (resource_id_type is int) and ("id" not in arg_name):
                pass

            elif resource_id_type is str:
                resource_id = arg_value

    if resource_id is None:
        raise CacheIdentificationInferenceError

    return resource_id


def _extract_data_inside_brackets(input_string: str) -> list[str]:
    """Извлекает данные внутри фигурных скобок из заданной строки, используя регулярные выражения.

    Параметры
    ---------
    input_string: str
        Входная строка, в которой нужно найти данные, заключенные в фигурные скобки.

    Возвращает
    ----------
    List[str]
        Список строк, содержащих данные, найденные внутри фигурных скобок во входной строке.

    Пример
    ------
    >>> _extract_data_inside_brackets("The {quick} brown {fox} jumps over the {lazy} dog.")
    ['quick', 'fox', 'lazy']
    """
    data_inside_brackets = re.findall(r"{(.*?)}", input_string)
    return data_inside_brackets


def _construct_data_dict(
    data_inside_brackets: list[str], kwargs: dict[str, Any]
) -> dict[str, Any]:
    """Создает словарь на основе данных внутри скобок и ключевых аргументов.

    Параметры
    ---------
    data_inside_brackets: List[str]
        Список ключей внутри скобок.
    kwargs: Dict[str, Any]
        Словарь ключевых аргументов.

    Возвращает
    ----------
    Dict[str, Any]: Словарь с ключами из data_inside_brackets и соответствующими значениями из kwargs.
    """
    data_dict = {}
    for key in data_inside_brackets:
        data_dict[key] = kwargs[key]
    return data_dict


def _format_prefix(prefix: str, kwargs: dict[str, Any]) -> str:
    """Форматирует префикс, используя ключевые аргументы.

    Параметры
    ----------
    prefix: str
        Шаблон префикса для форматирования.
    kwargs: Dict[str, Any]
        Словарь ключевых аргументов.

    Возвращает
    ----------
    str: Отформатированный префикс.
    """
    data_inside_brackets = _extract_data_inside_brackets(prefix)
    data_dict = _construct_data_dict(data_inside_brackets, kwargs)
    formatted_prefix = prefix.format(**data_dict)
    return formatted_prefix


def _format_extra_data(
    to_invalidate_extra: dict[str, str], kwargs: dict[str, Any]
) -> dict[str, Any]:
    """Форматирует дополнительные данные на основе предоставленных шаблонов и ключевых аргументов.

    Эта функция принимает словарь шаблонов и их соответствующих значений и словарь ключевых аргументов.
    Она форматирует шаблоны с соответствующими значениями из ключевых аргументов и возвращает словарь
    где ключи являются отформатированными шаблонами, а значения являются соответствующими значениями ключевых аргументов.

    Параметры
    ----------
    to_invalidate_extra: Dict[str, str]
        Словарь, где ключи являются шаблонами, а значения являются соответствующими значениями.
    kwargs: Dict[str, Any]
        Словарь ключевых аргументов.

    Возвращает
    ----------
        Dict[str, Any]: Словарь, где ключи являются отформатированными шаблонами,
        а значения являются соответствующими значениями ключевых аргументов.
    """
    formatted_extra = {}
    for prefix, id_template in to_invalidate_extra.items():
        formatted_prefix = _format_prefix(prefix, kwargs)
        id = _extract_data_inside_brackets(id_template)[0]
        formatted_extra[formatted_prefix] = kwargs[id]

    return formatted_extra


async def _delete_keys_by_pattern(pattern: str) -> None:
    """Удаляет ключи из Redis, которые соответствуют заданному шаблону, используя команду SCAN.

    Эта функция итеративно сканирует пространство ключей Redis для ключей, соответствующих определенному шаблону
    и удаляет их. Она использует команду SCAN для эффективного поиска ключей, что более
    производительно по сравнению с командой KEYS, особенно для больших наборов данных.

    Функция сканирует пространство ключей в итеративном режиме с использованием подхода на основе курсора.
    Он получает пакет ключей, соответствующих шаблону на каждой итерации и удаляет их
    пока не останется соответствующих ключей.

    Параметры
    ----------
    pattern: str
        Шаблон для сопоставления ключей. Шаблон может включать подстановочные знаки,
        такие как '*' для сопоставления любой последовательности символов. Пример: 'user:*'

    Примечания
    ----------
    - Команда SCAN используется с количеством 100 для получения ключей пакетами.
      Это количество можно отрегулировать в зависимости от размера вашего набора данных и производительности Redis.

    - Функция использует команду delete для удаления ключей группами. Если набор данных
      чрезвычайно большой, рассмотрите возможность реализации дополнительной логики для обработки удаления
      более эффективно.

    - Будьте осторожны с шаблонами, которые могут соответствовать большому количеству ключей, так как удаление
      множества ключей одновременно может повлиять на производительность сервера Redis.
    """
    if redis_client.client is None:
        raise MissingClientError

    cursor = 0  # Начинаем с курсора 0
    while True:
        cursor, keys = await redis_client.client.scan(cursor, match=pattern, count=100)
        if keys:
            await redis_client.client.delete(*keys)
        if cursor == 0:  # Когда курсор возвращается к 0, сканирование завершено
            break


def cache(  # noqa:PLR0913
    key_prefix: str,
    resource_id_name: Any = None,
    expiration: int = settings.redis_cache.CACHE_EXPIRATION,
    resource_id_type: type | tuple[type, ...] = int,
    to_invalidate_extra: dict[str, Any] | None = None,
    pattern_to_invalidate_extra: list[str] | None = None,
) -> Callable:
    """Декоратор кэша для FastAPI конечных точек.

    Этот декоратор позволяет кэшировать результаты функций FastAPI конечных точек для улучшения времени ответа
    и снижения нагрузки на приложение за счет хранения и получения данных в кэше.

    Параметры
    ----------
    key_prefix: str
        Уникальный префикс для идентификации ключа кэша.
    resource_id_name: Any, optional
        Имя аргумента ID ресурса в декорированной функции. Если предоставлено, оно используется непосредственно;
        в противном случае ID ресурса извлекается из аргументов функции.
    expiration: int, optional
        Время истечения кэшированных данных в секундах. По умолчанию 3600 секунд (1 час).
    resource_id_type: Union[type, Tuple[type, ...]], default int
        Ожидаемый тип ID ресурса.
        Это может быть один тип (например, int) или кортеж типов (например, (int, str)).
        По умолчанию int. Это используется только в том случае, если resource_id_name не предоставлено.
    to_invalidate_extra: Dict[str, Any] | None, optional
        Словарь, где ключи являются префиксами ключа кэша, а значениями являются шаблоны для суффиксов ключа кэша.
        Эти ключи недействительны, когда декорированная функция вызывается методом, отличным от GET.
    pattern_to_invalidate_extra: List[str] | None, optional
        Список строковых шаблонов для ключей кэша, которые должны быть недействительными, когда декорированная функция вызывается.
        Это позволяет групповому удалению ключей кэша на основе сопоставления шаблона.

    Возвращает
    ----------
    Callable
        Декоратор функции, который можно применить к функциям FastAPI конечных точек.

    Пример использования
    -------------

    ```python
    from fastapi import FastAPI, Request
    from my_module import cache  # Замените на ваш фактический модуль и импорты

    app = FastAPI()

    # Определите пример конечной точки с кэшированием
    @app.get("/sample/{resource_id}")
    @cache(key_prefix="sample_data", expiration=3600, resource_id_type=int)
    async def sample_endpoint(request: Request, resource_id: int):
        # Ваш код конечной точки здесь
        return {"data": "your_data"}
    ```

    Этот декоратор кэширует данные ответа функции конечной точки, используя уникальный ключ кэша.
    Кэшированные данные извлекаются для запросов GET, и кэш недействителен для других типов запросов.

    Расширенный пример использования
    -------------
    ```python
    from fastapi import FastAPI, Request
    from my_module import cache

    app = FastAPI()


    @app.get("/users/{user_id}/items")
    @cache(key_prefix="user_items", resource_id_name="user_id", expiration=1200)
    async def read_user_items(request: Request, user_id: int):
        # Конечная точка логики для получения элементов пользователя
        return {"items": "user specific items"}


    @app.put("/items/{item_id}")
    @cache(
        key_prefix="item_data",
        resource_id_name="item_id",
        to_invalidate_extra={"user_items": "{user_id}"},
        pattern_to_invalidate_extra=["user_*_items:*"],
    )
    async def update_item(request: Request, item_id: int, data: dict, user_id: int):
        # Логика обновления элемента
        # Недействительный кэш для конкретного элемента и всех кэшей для пользовательских элементов
        return {"status": "updated"}
    ```

    В этом примере:
    - Когда читаются элементы пользователя, ответ кэшируется под ключом, сформированным с префиксом 'user_items' и 'user_id'.
    - Когда обновляется элемент, кэш для этого конкретного элемента (под 'item_data:item_id') и все кэши с ключами
      начинающимися с 'user_{user_id}_items:' недействительны. Параметр to_invalidate_extra конкретно предназначен
      для кэша пользовательских элементов списка,
      в то время как pattern_to_invalidate_extra позволяет групповому удалению всех ключей
      соответствующих шаблону 'user_*_items:*', охватывающему всех пользователей.

    Примечание
    ----------
    - resource_id_type используется только в том случае, если resource_id не передается.
    - `to_invalidate_extra` и `pattern_to_invalidate_extra` используются для недействительности кэша на методах, отличных от GET.
    - Использование `pattern_to_invalidate_extra` может быть ресурсоемким на больших наборах данных. Используйте его осторожно и
      рассмотрите потенциальный эффект на производительности Redis.
    """

    def wrapper(func: Callable) -> Callable:
        @functools.wraps(func)
        async def inner(request: Request, *args: Any, **kwargs: Any) -> Response:
            if redis_client.client is None:
                raise MissingClientError

            if resource_id_name:
                resource_id = kwargs[resource_id_name]
            else:
                resource_id = _infer_resource_id(
                    kwargs=kwargs, resource_id_type=resource_id_type
                )

            formatted_key_prefix = _format_prefix(key_prefix, kwargs)
            cache_key = f"{formatted_key_prefix}:{resource_id}"
            if request.method == "GET":
                if (
                    to_invalidate_extra is not None
                    or pattern_to_invalidate_extra is not None
                ):
                    raise InvalidRequestError

                cached_data = await redis_client.client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data.decode())

            result = await func(request, *args, **kwargs)

            if request.method == "GET":
                serializable_data = jsonable_encoder(result)
                serialized_data = json.dumps(serializable_data)

                await redis_client.client.set(cache_key, serialized_data)
                await redis_client.client.expire(cache_key, expiration)

                serialized_data = json.loads(serialized_data)

            else:
                await redis_client.client.delete(cache_key)
                if to_invalidate_extra is not None:
                    formatted_extra = _format_extra_data(to_invalidate_extra, kwargs)
                    for prefix, id in formatted_extra.items():
                        extra_cache_key = f"{prefix}:{id}"
                        await redis_client.client.delete(extra_cache_key)

                if pattern_to_invalidate_extra is not None:
                    for pattern in pattern_to_invalidate_extra:
                        formatted_pattern = _format_prefix(pattern, kwargs)
                        await _delete_keys_by_pattern(formatted_pattern + "*")

            return result

        return inner

    return wrapper
