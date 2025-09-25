from pydantic import BaseModel, Field
from typing import Optional

class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=64)

class DepartmentCreate(DepartmentBase):
    role_id: int


class DepartmentUpdate(DepartmentBase):
    role_id: int


class DepartmentFilter(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=64)
    role_id: Optional[int] = None


class DepartmentRead(DepartmentBase):
    id: int
    role_id: int

    class Config:
        from_attributes = True

class DepartmentReadWithCount(DepartmentRead):
    count: int
