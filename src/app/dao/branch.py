from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.models.branch import Branch
from app.schemas.branch import Feedback, BranchRead
from sqlalchemy import select, text


class BranchDAO(BaseDAO):
    model = Branch


    @classmethod
    async def get_all(cls, session: AsyncSession):
        query = select(cls.model)
        result = await session.execute(query)
        branches = result.scalars().all()
        return [BranchRead.model_validate(branch) for branch in branches]

    @classmethod
    async def add_feedback(cls, session: AsyncSession, feedback: Feedback) -> BranchRead:
        query = text(
            """
            UPDATE branchs
            SET 
                rating = (rating * voice_count + :new_rating) / (voice_count + 1),
                voice_count = voice_count + 1
            WHERE id = :branch_id
            RETURNING id, name, rating, voice_count
            """
        )
        result = await session.execute(query, {
            "branch_id": feedback.branch_id,
            "new_rating": feedback.rating,
        })
        row = result.mappings().one()
        await session.commit()
        return BranchRead(**row)
