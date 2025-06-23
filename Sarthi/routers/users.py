from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID, uuid4  # ✅ Import uuid4
from db.session import get_db
from db.model import User
from schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)  # ✅ Fixed endpoint path
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user with auto-generated UUID"""
    try:
        # Check if email already exists
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_email = result.scalar_one_or_none()
        
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # ✅ AUTO-GENERATE UUID FOR NEW USER
        new_user_id = uuid4()
        
        # Create new user with auto-generated UUID
        new_user = User(
            user_id=new_user_id,  # ✅ Use auto-generated UUID
            name=user_data.name,
            email=user_data.email,
            phone_number=user_data.phone_number,
            user_type=user_data.user_type,
            proficiency_score=user_data.proficiency_score
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/", response_model=List[UserResponse])  # ✅ Changed to UserResponse for consistency
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all users"""
    result = await db.execute(
        select(User).where(User.status == 1).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return users

@router.get("/{user_id}", response_model=UserResponse)  # ✅ Changed to UserResponse
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get user by ID"""
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.get("/email/{email}", response_model=UserResponse)  # ✅ Changed to UserResponse
async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """Get user by email"""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing user"""
    try:
        # Get existing user
        result = await db.execute(select(User).where(User.user_id == user_id))
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if email update conflicts with another user
        if user_update.email and user_update.email != existing_user.email:
            result = await db.execute(select(User).where(User.email == user_update.email))
            email_conflict = result.scalar_one_or_none()
            if email_conflict:
                raise HTTPException(status_code=400, detail="Email already registered")
        
        # Update user fields
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(existing_user, field, value)
        
        await db.commit()
        await db.refresh(existing_user)
        
        return existing_user
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")