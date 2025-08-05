from fastapi import APIRouter
from app.core.db import TransactionSessionDep
from app.dao.person import PersonDAO
from app.dao.department import DepartmentDAO
from app.schemas.person import PersonCreate, PersonRead, PersonFullRead, PersonExcel
from app.core.config import settings
from app.schemas import DataResponse
from fastapi import status, Query
from fastapi import File, Form, UploadFile
from app.core.exceptions import NotFoundException
from app.schemas.person import PersonFilter
from app.schemas import PaginatedListResponse, get_pagination
import os
from app.core.utils.create_zip import create_zip
import uuid


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
    save_path = f"storage/persons/{uuid.uuid4()}.{image.filename.split(".")[-1]}"
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
    "/get_by_id/{person_id}",
    response_model=DataResponse[PersonFullRead],
)
async def get_person_by_id(
    person_id: int,
    session=TransactionSessionDep,
):
    person = await PersonDAO.get_person_by_id(session=session, person_id=person_id)
    return DataResponse(data=person)
    
@router.get(
    "/get_all",
    response_model=PaginatedListResponse[PersonRead],
)
async def get_persons(
    role_id: int | None = None,
    department_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    session=TransactionSessionDep,
):
    db_persons_count = await PersonDAO.count(
        session=session,
        filters=PersonFilter(
            role_id=role_id,
            department_id=department_id,
        ),
    )
    db_persons = await PersonDAO.paginate(
        session=session,
        filters=PersonFilter(
            role_id=role_id,
            department_id=department_id,
        ),
        page=page,
        page_size=page_size,
        order_by="id",
        order_direction="desc",
    )
    return PaginatedListResponse(
        data=db_persons,
        pagination=get_pagination(
            total_count=db_persons_count,
            page=page,
            page_size=page_size,
        ),
    )

@router.get(
    "/get_excel",
    #response_model=DataResponse[List[PersonExcel]],
)
async def get_persons_excel(
    session=TransactionSessionDep,
):
    persons = await PersonDAO.get_persons_excel(session=session)
    path = await create_zip(persons_data=persons)
    return path
