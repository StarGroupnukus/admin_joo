import asyncio
import logging

import uvloop
from arq.worker import Worker

from app.core.config import settings
from app.core.db import db_helper
from app.core.services.eskiz.eskiz_client import AsyncEskizClient
from app.schemas.person import PersonExcel
from typing import List
from shutil import make_archive
import os
import shutil
from app.core.utils.create_zip import create_excel
from app.core.config import SOURCE_DIR

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logger = logging.getLogger(__name__)


# -------- background tasks --------


async def create_zip(
    ctx: Worker,
    persons_data: List[PersonExcel]):
    for person in persons_data:
        os.makedirs(f"{SOURCE_DIR}/storage/tmp", exist_ok=True)
        os.makedirs(f"{SOURCE_DIR}/storage/tmp/images", exist_ok=True)
        shutil.copyfile(
            person.image_url,
            f"{SOURCE_DIR}/storage/tmp/images/{person.id}.{person.image_url.split(".")[-1]}",
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


async def send_sms_task(
    ctx: Worker,
    phone_number: str,
    message: str,
):
    try:
        client: AsyncEskizClient = ctx["eskiz_client"]
        result = await client.send_sms(phone_number, message)
        return {
            "status": "success",
            "result": result.model_dump(),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


# -------- base functions --------
async def startup(ctx: Worker) -> None:
    logging.info("Worker Started")
    ctx["eskiz_client"] = AsyncEskizClient(
        email=settings.eskiz.EMAIL,
        password=settings.eskiz.PASSWORD,
    )
    # await ctx["eskiz_client"].login()

    ctx["session"] = await anext(db_helper.session_getter())


async def shutdown(ctx: Worker) -> None:
    logging.info("Worker end")
