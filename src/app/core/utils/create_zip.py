from typing import List
import pandas as pd
from app.schemas.person import PersonExcel

async def create_excel(file_path: str, persons_data: List[PersonExcel]):
    data = [
        {
            "Идентификатор": p.id,
            "Имя": p.first_name.upper(),
            "Фамилия": p.last_name.upper(),
            "Департамент": p.department,
            "Начало срока действия": p.created_at,
            "Конец срока действия": p.extented_at,
        } for p in persons_data
    ]
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    return file_path

