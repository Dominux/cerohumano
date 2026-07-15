from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.common.database import get_db  # Your pure async generator helper dependency
from app.schemas import CeroHumanoCreate, CeroHumanoResponse
from app.services import CeroHumanoService


router = APIRouter(prefix="/cerohumanos", tags=["CeroHumano Profiles"])


@router.post(
    "",
    response_model=CeroHumanoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new CeroHumano profile record"
)
async def create_cerohumano(
    payload: CeroHumanoCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Validates incoming request fields, tracks database constraint configurations,
    and handles unique collision errors elegantly.
    """
    try:
        # Convert Pydantic fields into a dictionary payload for the base repository layer
        new_profile = await CeroHumanoService(db).create(payload.model_dump())
        return new_profile

    except IntegrityError as e:
        # Gracefully capture unique constraint violations (username, trigger_word, lora_name)
        # preventing 500 server crashes at the controller border layer
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A profile with this username, trigger word, or lora name already exists."
        )


@router.get(
    "",
    response_model=list[CeroHumanoResponse],
    summary="Retrieve a list of Cero Humano profiles"
)
async def list_cerohumanos(db: AsyncSession = Depends(get_db)):
    """
    Fetches a paginated array collection of user profiles.
    Supports optional dictionary filtering mapped natively via the ORM repository layer.
    """
    return await CeroHumanoService(db).list()
