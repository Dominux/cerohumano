import uuid

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema


# 1. The structural Request Contract payload
class CeroHumanoCreate(BaseModel):
    username: str = Field(..., max_length=255, description="Unique identity handle")
    first_name: str = Field(..., max_length=255)
    last_name: str = Field(..., max_length=255)
    trigger_word: str = Field(..., max_length=255, description="Unique generation trigger")
    lora_name: str = Field(..., max_length=255, description="Unique backend LoRA config file target")


# 2. The structural Response output serialization contract
class CeroHumanoResponse(BaseSchema, CeroHumanoCreate):
    # Inherits id, created_at, and from_attributes automatically from BaseSchema!

    # Optional field matching profile_picture_id
    profile_picture_id: uuid.UUID | None = Field(default=None)
