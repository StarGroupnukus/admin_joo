from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.branch import BranchRead
from app.schemas.branch import Feedback
from app.dao import BaseDAO
from app.models.branch import Branch


class BranchDAO(BaseDAO):
    model = Branch

    @classmethod
    async def get_all(cls, session: AsyncSession):
        query = text(
            """
            SELECT 
                id, 
                name,
                rating_1_count,
                rating_2_count,
                rating_3_count,
                rating_4_count,
                rating_5_count,
                CASE 
                    WHEN (rating_1_count + rating_2_count + rating_3_count + rating_4_count + rating_5_count) = 0 
                    THEN 0
                    ELSE (
                        (1 * rating_1_count +
                         2 * rating_2_count +
                         3 * rating_3_count +
                         4 * rating_4_count +
                         5 * rating_5_count
                        )::float
                        /
                        (rating_1_count + rating_2_count + rating_3_count + rating_4_count + rating_5_count)
                    )
                END AS rating
            FROM branches
            """
        )
        result = await session.execute(query)
        branches = result.mappings().all()
        return [BranchRead(**branch) for branch in branches]

    @classmethod
    async def add_feedback(
        cls, session: AsyncSession, feedback: Feedback
    ) -> BranchRead:
        # динамически выбираем, какой счётчик увеличить
        query = text(
            f"""
            UPDATE branches
            SET rating_{feedback.rating}_count = rating_{feedback.rating}_count + 1
            WHERE id = :branch_id
            RETURNING 
                id, 
                name,
                rating_1_count,
                rating_2_count,
                rating_3_count,
                rating_4_count,
                rating_5_count,
                CASE 
                    WHEN (rating_1_count + rating_2_count + rating_3_count + rating_4_count + rating_5_count) = 0 
                    THEN 0
                    ELSE (
                        (1 * rating_1_count +
                         2 * rating_2_count +
                         3 * rating_3_count +
                         4 * rating_4_count +
                         5 * rating_5_count
                        )::float
                        /
                        (rating_1_count + rating_2_count + rating_3_count + rating_4_count + rating_5_count)
                    )
                END AS rating
            """
        )
        result = await session.execute(query, {"branch_id": feedback.branch_id})
        row = result.mappings().one()
        await session.commit()
        return BranchRead(**row)
