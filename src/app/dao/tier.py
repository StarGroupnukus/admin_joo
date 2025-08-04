from app.dao import BaseDAO
from app.models.tier import Tier


class TierDAO(BaseDAO):
    model = Tier
