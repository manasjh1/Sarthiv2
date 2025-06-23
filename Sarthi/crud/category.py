from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from db.model import CategoryDict

async def get_category_by_id(db: AsyncSession, category_no: int) -> Optional[CategoryDict]:
    """Get category by category number/ID"""
    result = await db.execute(
        select(CategoryDict).where(CategoryDict.category_no == category_no)
    )
    return result.scalar_one_or_none()

async def get_category_by_name(db: AsyncSession, category_name: str) -> Optional[CategoryDict]:
    """Get category by name"""
    result = await db.execute(
        select(CategoryDict).where(CategoryDict.category_name == category_name)
    )
    return result.scalar_one_or_none()

async def get_categories_for_dropdown(db: AsyncSession) -> List[CategoryDict]:
    """Get all active categories for dropdown selection"""
    result = await db.execute(
        select(CategoryDict).where(CategoryDict.status == 1).order_by(CategoryDict.category_no)
    )
    return result.scalars().all()

async def validate_category_choice(db: AsyncSession, category_no: int) -> bool:
    """Validate if the selected category number exists and is active"""
    category = await get_category_by_id(db, category_no)
    return category is not None and category.status == 1