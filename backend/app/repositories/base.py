import uuid
from typing import Any, Generic, Iterable, Type, TypeVar, Sequence

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    model: Type[ModelType]

    def __init__(self, session: AsyncSession):
        """
        Base repository providing generic CRUD operations.
        :param model: The SQLAlchemy model class (e.g., PostModel)
        :param session: The active SQLAlchemy Session instance
        """
        self.session = session

    async def get_by_id(self, id_: uuid.UUID) -> ModelType | None:
        """Fetch a single record by its UUID primary key."""
        return await self.session.get(self.model, id_)

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None
    ) -> Sequence[ModelType]:
        """Fetch records with pagination and high-level ORM filtering."""
        stmt = sa.select(self.model)

        if filters:
            # Safely unpack valid dictionary keys natively into ORM expressions
            valid_filters = {k: v for k, v in filters.items() if hasattr(self.model, k)}
            stmt = stmt.filter_by(**valid_filters)

        stmt = stmt.offset(skip).limit(limit)

        # Execute asynchronously using scalars directly
        result = await self.session.scalars(stmt)
        return result.all()

    async def create(self, obj_data: dict[str, Any]) -> ModelType:
        """Instantiate and persist a new model record asynchronously."""
        db_obj = self.model(**obj_data)
        self.session.add(db_obj)

        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        obj_id: uuid.UUID,
        update_data: dict[str, Any],
        refresh_attrs: Iterable[str] | None = None
    ) -> ModelType:
        # 1. Fetch it fresh inside this session
        db_obj = await self.session.get(self.model, obj_id)
        if not db_obj:
            raise ValueError("Object not found")

        # 2. Apply updates
        for key, value in update_data.items():
            setattr(db_obj, key, value)

        # 3. Commit and Refresh will now work perfectly
        await self.session.commit()
        await self.session.refresh(db_obj, attribute_names=refresh_attrs)
        return db_obj

    async def delete(self, id_: uuid.UUID) -> bool:
        """Remove a record by its UUID from the database entirely."""
        stmt = sa.delete(self.model).where(self.model.id == id_)

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount > 0
