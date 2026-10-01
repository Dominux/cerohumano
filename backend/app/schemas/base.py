import datetime
import uuid

from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    id: uuid.UUID
    created_at: datetime.datetime

    # Enable automatic extraction from SQLAlchemy ORM objects
    model_config = ConfigDict(from_attributes=True)
