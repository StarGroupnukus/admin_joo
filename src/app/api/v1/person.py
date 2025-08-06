import os
import uuid

from fastapi import APIRouter, File, Form, Query, UploadFile, status

from app.core.config import settings
from app.core.db import TransactionSessionDep
from app.core.exceptions import NotFoundException
from app.core.utils.create_zip import create_zip
from app.dao.person import PersonDAO
from app.schemas import DataResponse, PaginatedListResponse, get_pagination
from app.schemas.person import (
    PersonCreate,
    PersonFilter,
    PersonFullRead,
    PersonRead,
    PersonUpdate,
)

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
    os.makedirs("storage/persons", exist_ok=True)
    save_path = f"storage/persons/{uuid.uuid4()}.{image.filename.split('.')[-1]}"
    with open(save_path, "wb") as buffer:
        buffer.write(await image.read())

    person_data = PersonCreate(
        first_name=first_name,
        last_name=last_name,
        department_id=department_id,
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
    department_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    session=TransactionSessionDep,
):
    db_persons_count = await PersonDAO.count(
        session=session,
        filters=PersonFilter(
            department_id=department_id,
        ),
    )
    db_persons = await PersonDAO.paginate(
        session=session,
        filters=PersonFilter(
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
    # response_model=DataResponse[List[PersonExcel]],
)
async def get_persons_excel(
    session=TransactionSessionDep,
):
    persons = await PersonDAO.get_persons_excel(session=session)
    path = await create_zip(persons_data=persons)
    return path


@router.delete(
    "/delete/{person_id}",
    status_code=status.HTTP_200_OK,
    response_model=DataResponse[int],
)
async def delete_person(
    person_id: int,
    session=TransactionSessionDep,
):
    db_person = await PersonDAO.find_one_or_none_by_id(
        session=session,
        data_id=person_id,
    )
    if db_person is None:
        raise NotFoundException(
            message="Person not found",
        )
    os.remove(db_person.image_url)
    await PersonDAO.delete(
        session=session,
        filters=PersonFilter(
            id=person_id,
        ),
    )

    return DataResponse(data=person_id)


@router.put(
    "/update/{person_id}",
    status_code=status.HTTP_200_OK,
    response_model=DataResponse[PersonRead],
)
async def update_person(
    person_id: int,
    update_data: PersonUpdate,
    session=TransactionSessionDep,
):
    db_person = await PersonDAO.find_one_or_none_by_id(
        session=session,
        data_id=person_id,
    )
    if db_person is None:
        raise NotFoundException(
            message="Person not found",
        )

    await PersonDAO.update(
        session=session,
        filters=PersonFilter(
            id=person_id,
        ),
        values=update_data,
    )
    updated_person = await PersonDAO.find_one_or_none_by_id(
        session=session,
        data_id=person_id,
    )
    return DataResponse(data=updated_person)
