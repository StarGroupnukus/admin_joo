import os
import shutil
from shutil import make_archive
from typing import List

import pandas as pd

from app.schemas.person import PersonExcel


async def create_excel(file_path: str, persons_data: List[PersonExcel]):
    data = [
        {
            "Идентификатор": p.id,
            "Имя": p.first_name,
            "Фамилия": p.last_name,
            "Департамент": p.department,
            "Начало срока действия": p.created_at,
            "Конец срока действия": p.extented_at,
        }
        for p in persons_data
    ]
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    return file_path


async def create_zip(persons_data: List[PersonExcel]):
    for person in persons_data:
        os.makedirs("storage/tmp", exist_ok=True)
        os.makedirs("storage/tmp/images", exist_ok=True)
        shutil.copyfile(
            person.image_url,
            f"storage/tmp/images/{person.id}.{person.image_url.split('.')[-1]}",
        )
    await create_excel(file_path="storage/tmp/person.xlsx", persons_data=persons_data)
    make_archive("storage/person", "zip", "storage/tmp")
    shutil.rmtree("storage/tmp")
    return "storage/person.zip"
