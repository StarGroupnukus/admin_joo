from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

class BranchBase(BaseModel):
    name: str

class BranchCreate(BranchBase):
    pass

class BranchRead(BranchBase):
    id: int
    rating: float
    voice_count: int
    
    model_config = ConfigDict(from_attributes=True)

class Feedback(BaseModel):
    branch_id: int
    rating: float = Field(ge=1, le=5)

class BranchFilter(BaseModel):
    id : int | None = None
    name : str | None = None
