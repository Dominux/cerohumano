import uuid
from typing import Generic, Type, TypeVar, Sequence, Any

from sqlalchemy.orm import Session

from app.common.database import Base
from app.repositories.base import BaseRepository


ModelType = TypeVar("ModelType", bound=Base)


class BaseService(Generic[ModelType]):
    repository_class: Type[BaseRepository[ModelType]]

    def __init__(self, session: Session):
        """
        Base service layer handling generic domain business logic rules.
        """
        self.repository = self.repository_class(session)

    def get_by_id(self, id_: uuid.UUID) -> ModelType | None:
        """Business wrapper to retrieve a record by its UUID."""
        # You can add custom domain exception handlers here if an object is missing
        return self.repository.get_by_id(id_)

    def list(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Business wrapper to retrieve paginated records."""
        return self.repository.list(skip=skip, limit=limit)

    def create(self, payload: dict[str, Any]) -> ModelType:
        """Business validation wrapper to insert a new domain record."""
        # Clean data payload parsing or default business field logic belongs here
        return self.repository.create(payload)

    def update(self, id_: uuid.UUID, update_data: dict[str, Any]) -> ModelType | None:
        """Locates a specific object record and performs structural field mutations."""
        db_obj = self.repository.get_by_id(id_)
        if not db_obj:
            return None
        return self.repository.update(db_obj, update_data)

    def delete(self, id_: uuid.UUID) -> bool:
        """Completely eliminates an object domain record from database state storage."""
        return self.repository.delete(id_)
