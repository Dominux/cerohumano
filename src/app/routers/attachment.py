import uuid

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.repositories import CeroHumanoRepository
from app.schemas import AttachmentResponse
from app.services import AttachmentService


router = APIRouter(prefix="/attachments", tags=["Attachments & Media"])


@router.post(
    "/profile-picture/{author_id}",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a user profile picture avatar"
)
async def upload_profile_picture(
    author_id: uuid.UUID,
    file: UploadFile = File(..., description="The binary image file (png, jpg, jpeg)"),
    db: AsyncSession = Depends(get_db)
):
    # 1. Validation: Verify the targeted CeroHumano account actually exists first
    cerohumano = await CeroHumanoRepository(db).get_by_id(author_id)

    if not cerohumano:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The targeted CeroHumano account user profile does not exist."
        )

    # 2. File verification filter
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format type. Only image uploads are permitted for avatars."
        )

    # 3. Creating
    payload = {'author_id': author_id}
    content = await file.read()
    attach = await AttachmentService(db).create(payload, content=content)

    # 4. Assigning as a profile picture
    await CeroHumanoRepository(db).update(cerohumano.id, {'profile_picture': attach})

    return AttachmentResponse.model_validate(attach)
