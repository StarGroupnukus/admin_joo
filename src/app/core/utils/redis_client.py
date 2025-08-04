from redis.asyncio import ConnectionPool, Redis

# from ..config import settings

pool: ConnectionPool | None = None
client: Redis | None = None

# Инициализация пула соединений и клиента Redis
# pool = ConnectionPool.from_url(settings.redis_client.REDIS_URL)
# client = Redis(connection_pool=pool)
