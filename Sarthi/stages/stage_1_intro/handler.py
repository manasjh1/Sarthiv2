from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.model import Reflection, User, Message
from crud.category import get_category_by_name, get_category_by_id, validate_category_choice, get_categories_for_dropdown
from crud.stage import get_stage_by_no
from orchestrator.state_machine import get_next_stage
from stages.stage_1_intro.logic import determine_mode
from prompts.prompt_library import prompt_library

async def start_reflection(user_id: UUID, db: AsyncSession):
    """Start reflection workflow at Stage 1 (Category Selection)"""
    
    # ✅ FIX: Properly get user by UUID
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise ValueError(f"User with ID {user_id} not found")

    # ✅ FIX: Check if user already has an active reflection
    existing_reflection_result = await db.execute(
        select(Reflection).where(
            Reflection.giver_user_id == user_id,
            Reflection.status == 1
        ).order_by(Reflection.created_at.desc())
    )
    existing_reflection = existing_reflection_result.scalar_one_or_none()
    
    if existing_reflection:
        # Return existing reflection info instead of creating new one
        stage = await get_stage_by_no(db, existing_reflection.stage_no)
        return {
            "reflection_id": existing_reflection.reflection_id,
            "stage_no": existing_reflection.stage_no,
            "stage_name": stage.stage_name if stage else f"STAGE_{existing_reflection.stage_no}",
            "prompt": prompt_library.get(existing_reflection.stage_no, {}).get("prompt", "Continue your reflection"),
            "mode": existing_reflection.mode.value,
            "message": "Resuming existing reflection"
        }

    # Get stage 1 info
    stage_1 = await get_stage_by_no(db, 1)
    if not stage_1:
        raise ValueError("Stage 1 not found in stages_dict")

    mode = await determine_mode(user.proficiency_score)
    
    # ✅ FIX: Get the first available category (default to category 1 - feedback)
    # Since users will select category via dropdown, we'll use a default category for now
    default_category = await get_category_by_id(db, 1)  # Default to category 1 (feedback)
    if not default_category:
        # Fallback: get any available category
        categories = await get_categories_for_dropdown(db)
        if not categories:
            raise ValueError("No categories available in the system")
        default_category = categories[0]
    
    # ✅ AUTO-GENERATE REFLECTION UUID
    new_reflection_id = uuid4()

    # Create reflection with proper validation
    new_reflection = Reflection(
        reflection_id=new_reflection_id,
        giver_user_id=user_id,
        stage_no=1,
        category_no=default_category.category_no,
        mode=mode,
        status=1
    )
    db.add(new_reflection)
    
    try:
        await db.commit()
        await db.refresh(new_reflection)
    except Exception as e:
        await db.rollback()
        raise ValueError(f"Failed to create reflection: {str(e)}")

    try:
        # Get available categories for dropdown
        available_categories = await get_categories_for_dropdown(db)
        category_options = [
            {"id": cat.category_no, "name": cat.category_name} 
            for cat in available_categories
        ]

        return {
            "reflection_id": new_reflection.reflection_id,
            "stage_no": 1,
            "stage_name": stage_1.stage_name,
            "prompt": prompt_library[1]["prompt"],
            "mode": mode.value,
            "category_options": category_options  # Include dropdown options
        }
    except Exception as e:
        await db.rollback()
        raise ValueError(f"Failed to get categories: {str(e)}")

async def set_category(reflection_id: UUID, category_no, db: AsyncSession):
    """Set category by category number and advance to Stage 2"""
    
    # ✅ Handle both string and int inputs (temporary fix)
    try:
        if isinstance(category_no, str):
            category_no = int(category_no)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid category_no format: {category_no}. Must be an integer.")
    
    # ✅ FIX: Properly get reflection by UUID
    result = await db.execute(select(Reflection).where(Reflection.reflection_id == reflection_id))
    reflection = result.scalar_one_or_none()
    
    if not reflection:
        raise ValueError(f"Reflection with ID {reflection_id} not found")
    
    if reflection.stage_no != 1:
        raise ValueError(f"Category can only be set in Stage 1. Current stage: {reflection.stage_no}")

    # ✅ Validate category selection
    if not await validate_category_choice(db, category_no):
        raise ValueError(f"Invalid category selection: {category_no}")

    # Get the selected category
    category = await get_category_by_id(db, category_no)
    if not category:
        raise ValueError(f"Category with ID {category_no} not found")

    # Get stage 2 info
    stage_2 = await get_stage_by_no(db, 2)
    if not stage_2:
        raise ValueError("Stage 2 not found in stages_dict")

    # Update reflection
    reflection.category_no = category.category_no
    reflection.stage_no = 2

    # Create message record for category selection
    new_message = Message(
        text=f"Selected category: {category.category_name}",
        reflection_id=reflection_id,
        sender=1,  # User
        stage_no=1
    )
    db.add(new_message)
    
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise ValueError(f"Failed to set category: {str(e)}")

    return {
        "stage_no": 2,
        "stage_name": stage_2.stage_name,
        "prompt": prompt_library[2]["prompt"],
        "selected_category": category.category_name
    }

async def advance_stage(reflection_id: UUID, user_input: str, db: AsyncSession):
    """Advance through stages 2, 3, 4+"""
    
    # ✅ FIX: Properly get reflection by UUID
    result = await db.execute(select(Reflection).where(Reflection.reflection_id == reflection_id))
    reflection = result.scalar_one_or_none()
    
    if not reflection:
        raise ValueError(f"Reflection with ID {reflection_id} not found")

    current_stage = reflection.stage_no

    # Handle input based on current stage
    if current_stage == 2:
        reflection.name = user_input  # Store recipient name
    elif current_stage == 3:
        reflection.relation = user_input  # Store relationship
    elif current_stage == 4:
        reflection.reflection = user_input  # Store message content
    
    # Create message record
    new_message = Message(
        text=user_input,
        reflection_id=reflection_id,
        sender=1,  # User
        stage_no=current_stage
    )
    db.add(new_message)

    # Get next stage info
    next_info = get_next_stage(current_stage)
    if not next_info:
        # Workflow complete
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise ValueError(f"Failed to complete reflection: {str(e)}")
        return {"message": "Reflection workflow complete!"}

    # Get next stage from database
    next_stage = await get_stage_by_no(db, next_info["stage_no"])
    if not next_stage:
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise ValueError(f"Failed to complete reflection: {str(e)}")
        return {"message": "Reflection workflow complete!"}

    # Update reflection to next stage
    reflection.stage_no = next_info["stage_no"]
    
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise ValueError(f"Failed to advance stage: {str(e)}")

    return {
        "stage_no": next_info["stage_no"],
        "stage_name": next_stage.stage_name,
        "prompt": next_info["prompt"]
    }

# ✅ NEW: Helper function to get category options for frontend
async def get_category_options(db: AsyncSession):
    """Get category options for dropdown"""
    categories = await get_categories_for_dropdown(db)
    return [
        {"id": cat.category_no, "name": cat.category_name} 
        for cat in categories
    ]