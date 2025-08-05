from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass

class RoleFilter(RoleBase):
    id : int | None = None
    name : str | None = None
    
class RoleRead(RoleBase):
    id: int


    class Config:
        from_attributes = True
