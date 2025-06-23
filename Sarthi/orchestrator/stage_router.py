from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from stages.stage_1_intro.handler import start_reflection, set_category, advance_stage
from schemas import (
    StartReflectionInput,
    CategoryInput,
    NextStageInput, 
    ReflectionStartResponse,
    StageResponse
)

router = APIRouter(tags=["reflection-stages"])

@router.post("/reflection/start", response_model=ReflectionStartResponse)
async def api_start_reflection(
    data: StartReflectionInput,
    db: AsyncSession = Depends(get_db)
):
    """Start a new reflection workflow - begins at Stage 1 (Category Selection)"""
    try:
        result = await start_reflection(data.user_id, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the full error for debugging
        print(f"Unexpected error in start_reflection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/reflection/category", response_model=StageResponse)
async def api_set_category(
    data: CategoryInput,
    db: AsyncSession = Depends(get_db)
):
    """Set category and move to Stage 2 (Recipient Name)"""
    try:
        result = await set_category(data.reflection_id, data.category_name, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error in set_category: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/reflection/next", response_model=StageResponse)
async def api_next_stage(
    data: NextStageInput,
    db: AsyncSession = Depends(get_db)
):
    """Advance to next stage with user input"""
    try:
        result = await advance_stage(data.reflection_id, data.user_input, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error in advance_stage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ✅ ADD: Get reflection status endpoint
@router.get("/reflection/{reflection_id}")
async def get_reflection_status(reflection_id: str, db: AsyncSession = Depends(get_db)):
    """Get current reflection status"""
    from uuid import UUID
    from sqlalchemy.future import select
    from db.model import Reflection
    
    try:
        reflection_uuid = UUID(reflection_id)
        result = await db.execute(select(Reflection).where(Reflection.reflection_id == reflection_uuid))
        reflection = result.scalar_one_or_none()
        
        if not reflection:
            raise HTTPException(status_code=404, detail="Reflection not found")
        
        return {
            "reflection_id": str(reflection.reflection_id),
            "stage_no": reflection.stage_no,
            "category_no": reflection.category_no,
            "name": reflection.name,
            "relation": reflection.relation,
            "reflection": reflection.reflection,
            "status": reflection.status
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid reflection ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))