from fastapi import APIRouter
from app.core.db import TransactionSessionDep
from app.dao.person import PersonDAO
from app.dao.department import DepartmentDAO
from app.schemas.person import PersonCreate, PersonRead, PersonFullRead
from app.core.config import settings
from app.schemas import DataResponse
from fastapi import status
from fastapi import File, Form, UploadFile
from app.core.exceptions import NotFoundException
import os
router = APIRouter(
    prefix=settings.api.v1.persons,
    tags=["Persons"],
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DataResponse[PersonRead],
)
async def create_person(
    first_name: str = Form(...),
    last_name: str = Form(...),
    department_id: int = Form(...),
    image: UploadFile = File(...),
    session=TransactionSessionDep,
):
    role_id = await DepartmentDAO.get_role_id(session=session, department_id=department_id)
    if role_id is None:
        raise NotFoundException(
            message="Department not found",
        )

    os.makedirs("storage/persons", exist_ok=True)
    save_path = f"storage/persons/{image.filename}"
    with open(save_path, "wb") as buffer:
        buffer.write(await image.read())

    person_data = PersonCreate(
        first_name=first_name,
        last_name=last_name,
        department_id=department_id,
        role_id=role_id,
        image_url=save_path,
    )

    person = await PersonDAO.add(session=session, values=person_data)

    return DataResponse(data=PersonRead.model_validate(person))

@router.get(
    "/{person_id}",
    response_model=DataResponse[PersonFullRead],
)
async def get_person_by_id(
    person_id: int,
    session=TransactionSessionDep,
):
    person = await PersonDAO.get_person_by_id(session=session, person_id=person_id)
    return DataResponse(data=person)
    