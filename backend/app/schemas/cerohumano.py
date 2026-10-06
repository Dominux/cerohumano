import uuid

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema
from app.models.cerohumano import CeroHumanoCupDescription



class CeroHumanoCupDescriptionSchema(BaseModel):
    min_cup: CeroHumanoCupDescription | None = Field(description="Minimal cup for cerohumano", default=None)


# 1. The structural Request Contract payload
class CeroHumanoCreate(CeroHumanoCupDescriptionSchema):
    username: str = Field(..., max_length=255, description="Unique identity handle")
    first_name: str = Field(..., max_length=255)
    last_name: str = Field(..., max_length=255)
    trigger_word: str = Field(..., max_length=255, description="Unique generation trigger")
    lora_name: str | None = Field(default=None, max_length=255, description="Unique backend LoRA config file target")


# 2. The structural Response output serialization contract
class CeroHumanoResponse(BaseSchema, CeroHumanoCreate):
    # Inherits id, created_at, and from_attributes automatically from BaseSchema!

    # Optional field matching profile_picture_id
    profile_picture_id: uuid.UUID | None = Field(default=None)


class CeroHumanoSetCup(CeroHumanoCupDescriptionSchema, BaseSchema):
    ...
