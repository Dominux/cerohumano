from typing import Any, Sequence

import sqlalchemy as sa

from app.models import PostModel
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[PostModel]):
    model = PostModel

    async def list_feed_posts(
        self,
        skip: int = 0,
        limit: int = 10,
        filters: dict[str, Any] | None = None
    ) -> Sequence[PostModel]:
        """Fetch posts with multiple file attachments pre-loaded via joined load configuration."""
        # Eagerly load the attachments relationship to prevent N+1 query bottlenecks
        stmt = (
            sa.select(self.model)
            .options(
                sa.orm.joinedload(self.model.attachments),
                sa.orm.joinedload(self.model.author),
            )
            .offset(skip)
            .limit(limit)
        )

        if filters:
            valid_filters = {k: v for k, v in filters.items() if hasattr(self.model, k)}
            stmt = stmt.filter_by(**valid_filters)

        stmt = stmt.offset(skip).limit(limit)

        result = await self.session.scalars(stmt)
        return result.unique().all()

