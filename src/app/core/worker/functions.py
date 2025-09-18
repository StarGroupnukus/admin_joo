import asyncio
import logging
import os
import shutil
from shutil import make_archive
from typing import List

import uvloop
from arq.worker import Worker

from app.core.config import SOURCE_DIR
from app.core.db import db_helper
from app.core.utils.create_zip import create_excel
from app.schemas.person import PersonExcel

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logger = logging.getLogger(__name__)


# -------- background tasks --------


async def create_zip(ctx: Worker, persons_data: List[PersonExcel]):
    zip_path = f"{SOURCE_DIR}/storage/person.zip"
    tmp_dir = f"{SOURCE_DIR}/storage/tmp"

    # Удалить старый zip (если есть)
    try:
        os.remove(zip_path)
    except FileNotFoundError:
        pass

    # Создать временные папки один раз
    os.makedirs(f"{tmp_dir}/images", exist_ok=True)

    # Скопировать изображения
    for person in persons_data:
        shutil.copyfile(
            person.image_url,
            f"{tmp_dir}/images/{person.first_name.upper()}+{person.last_name.upper()}_{person.id}.{person.image_url.split('.')[-1]}",
        )

    # Создать Excel
    await create_excel(file_path=f"{tmp_dir}/person.xlsx", persons_data=persons_data)

    # Создать ZIP-архив
    make_archive(f"{SOURCE_DIR}/storage/person", "zip", tmp_dir)

    # Удалить временные файлы
    shutil.rmtree(tmp_dir)

    return zip_path


async def create_zip(
    ctx: Worker,
    persons_data: List[PersonExcel]):
    for person in persons_data:
        try:
            os.remove(f'{SOURCE_DIR}/storage/person.zip')
        except FileNotFoundError:
            pass
        os.makedirs(f"{SOURCE_DIR}/storage/tmp", exist_ok=True)
        os.makedirs(f"{SOURCE_DIR}/storage/tmp/images", exist_ok=True)
        shutil.copyfile(
            person.image_url,
            f"{SOURCE_DIR}/storage/tmp/images/{person.first_name.upper()}+{person.last_name.upper()}_{person.id}.{person.image_url.split(".")[-1]}",
        )
    await create_excel(file_path=f"{SOURCE_DIR}/storage/tmp/person.xlsx", persons_data=persons_data)
    make_archive(f"{SOURCE_DIR}/storage/person", "zip", f"{SOURCE_DIR}/storage/tmp")
    shutil.rmtree(f"{SOURCE_DIR}/storage/tmp")
    return f"{SOURCE_DIR}/storage/person.zip"


async def sample_background_task(
    ctx: Worker,
    message: str = "Hello",
    phone_number: str = "998999999999",
) -> None:
    await asyncio.sleep(5)
    logging.info(f"Sendind SMS to {phone_number}")
    return f"SMS message{message} had been sent to {phone_number}"


# -------- base functions --------
async def startup(ctx: Worker) -> None:
    logging.info("Worker Started")
    ctx["session"] = await anext(db_helper.session_getter())


async def shutdown(ctx: Worker) -> None:
    logging.info("Worker end")
