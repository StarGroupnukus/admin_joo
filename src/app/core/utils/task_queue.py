from arq.connections import ArqRedis

# from .redis_client import pool
# pool = ArqRedis(pool)

pool: ArqRedis | None = None
