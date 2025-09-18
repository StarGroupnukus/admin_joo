from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class BranchBase(BaseModel):
    name: str

class BranchCreate(BranchBase):
    pass

class BranchRead(BranchBase):
    id: int
    rating_1_count: int
    rating_2_count: int
    rating_3_count: int
    rating_4_count: int
    rating_5_count: int
    rating: float
    model_config = ConfigDict(from_attributes=True)

class Feedback(BaseModel):
    branch_id: int
    rating: int = Field(ge=1, le=5)

class BranchFilter(BaseModel):
    id : int | None = None
    name : str | None = None
