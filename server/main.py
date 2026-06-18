from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from app import models
from app.common import database


# Pydantic validation structures
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

app = FastAPI()

# Async GET endpoint
@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(database.get_db)):
    # Create an async selection statement
    stmt = select(models.GirlModel).where(models.GirlModel.id == user_id)
    result = await db.execute(stmt)
    db_user = result.scalars().first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Async POST endpoint
@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(database.get_db)):
    # Check for duplicate username asynchronously
    stmt = select(models.GirlModel).where(models.GirlModel.username == user.username)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = models.GirlModel(username=user.username, email=user.email)
    db.add(new_user)

    # Commit changes and refresh instance mapping asynchronously
    await db.commit()
    await db.refresh(new_user)
    return new_user
