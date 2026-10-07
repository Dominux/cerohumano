import uuid

from fastapi import APIRouter, File, Form, UploadFile, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.services import PostService
from app.schemas import PostWithAttachmentsResponse


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


@router.get(
    "",
    response_model=list[PostWithAttachmentsResponse],
    summary="List posts with multiple file attachments"
)
async def list_posts(
    limit: int = 10,
    offset: int = 0,
    author_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db)
):
    filters = {}
    if author_id:
        filters['author_id'] = author_id
    return await PostService(db).list_posts(
        limit=limit,
        offset=offset,
        filters=filters,
    )
