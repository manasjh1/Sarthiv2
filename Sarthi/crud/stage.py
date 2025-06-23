from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from db.model import StageDict

async def get_stage_by_no(db: AsyncSession, stage_no: int) -> Optional[StageDict]:
    result = await db.execute(
        select(StageDict).where(StageDict.stage_no == stage_no)
    )
    return result.scalar_one_or_none()

async def get_stages(db: AsyncSession) -> List[StageDict]:
    result = await db.execute(
        select(StageDict).where(StageDict.status == 1)
    )
    return result.scalars().all()