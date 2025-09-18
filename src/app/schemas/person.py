
from pydantic import BaseModel

from app.schemas.department import DepartmentRead
from app.schemas.role import RoleRead


class PersonBase(BaseModel):
    first_name: str
    last_name: str
    image_url: str
    department_id: int

    
class PersonCreate(PersonBase):
    pass


class PersonRead(PersonBase):
    id: int
    #department: DepartmentRead
    
    class Config:
        from_attributes = True

class PersonFilter(PersonBase):
    id : int | None = None
    first_name : str | None = None
    last_name : str | None = None
    image_url : str | None = None
    department_id : int | None = None

class PersonUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    department_id: int | None = None

class PersonFullRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    image_url: str
    department: DepartmentRead
    role: RoleRead

class PersonExcel(BaseModel):
    id: int
    first_name: str
    last_name: str
    image_url: str
    department: str
    created_at: str
    extented_at: str

class PersonImport(BaseModel):
    id: int
    first_name: str
    last_name: str
    image_url: str
    department_id: int
