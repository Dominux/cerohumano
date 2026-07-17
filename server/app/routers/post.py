import uuid

from fastapi import APIRouter, File, Form, UploadFile, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.services import PostService


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Upload multiple attachment files"
)
async def upload_post(
    files: list[UploadFile] = File(..., description="The binary image files (png, jpg, jpeg)"),
    author_id: uuid.UUID = Form(...),
    caption: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    return await PostService(db).upload_post(author_id, caption, files=files)
