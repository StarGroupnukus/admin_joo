from app.dao import BaseDAO
from app.models.rate_limit import RateLimit


class RateLimitDAO(BaseDAO):
    model = RateLimit
