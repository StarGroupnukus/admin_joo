from pydantic import BaseModel


class DepartmentBase(BaseModel):
    name: str


class DepartmentCreate(DepartmentBase):
    role_id: int


class DepartmentUpdate(DepartmentBase):
    role_id: int


class DepartmentFilter(DepartmentBase):
    id: int | None = None
    name: str | None = None
    role_id: int | None = None


class DepartmentRead(DepartmentBase):
    id: int
    role_id: int

    class Config:
        from_attributes = True
