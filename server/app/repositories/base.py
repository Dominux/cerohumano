import uuid
from typing import Generic, Type, TypeVar, Sequence

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.common.database import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    model: Type[ModelType]

    def __init__(self, session: Session):
        """
        Base repository providing generic CRUD operations.
        :param model: The SQLAlchemy model class (e.g., PostModel)
        :param session: The active SQLAlchemy Session instance
        """
        self.session = session

    def get_by_id(self, id_: uuid.UUID) -> ModelType | None:
        """Fetch a single record by its UUID primary key."""
        return self.session.get(self.model, id_)

    def list(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Fetch records with pagination configuration."""
        stmt = sa.select(self.model).offset(skip).limit(limit)
        return self.session.execute(stmt).scalars().all()

    def create(self, obj_data: dict) -> ModelType:
        """Instantiate and persist a new model record."""
        db_obj = self.model(**obj_data)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, update_data: dict) -> ModelType:
        """Update fields on an existing model record dynamically."""
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, id_: uuid.UUID) -> bool:
        """Remove a record by its UUID from the database entirely."""
        stmt = sa.delete(self.model).where(self.model.id == id_)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0
