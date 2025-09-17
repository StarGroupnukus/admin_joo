from pydantic import BaseModel
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
    rating: float