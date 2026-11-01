from typing import Any, Sequence
import uuid

import sqlalchemy as sa

from app.models import PostModel
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[PostModel]):
    model = PostModel

    async def list_posts_with_attachments(
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
            .order_by(self.model.created_at.desc())
        )

        if filters:
            valid_filters = {k: v for k, v in filters.items() if hasattr(self.model, k)}
            stmt = stmt.filter_by(**valid_filters)

        stmt = stmt.offset(skip).limit(limit)

        result = await self.session.scalars(stmt)
        return result.unique().all()

    async def get_post_with_attachments(self, post_id: uuid.UUID):
        stmt = (
            sa.select(self.model)
            .options(
                sa.orm.joinedload(self.model.attachments),
                sa.orm.joinedload(self.model.author),
            )
            .where(self.model.id == post_id)
        )

        result = await self.session.scalars(stmt)
        return result.unique().one()

    async def list_next_author_ids(self, amount: int):
        query = '''
            WITH slots AS (
                -- Dynamically generate N slots based on the passed parameter
                SELECT generate_series(1, :slots_count) AS slot_id
            ),
            author_post_counts AS (
                SELECT
                    c.id AS author_id,
                    COUNT(p.id) AS post_count
                FROM cerohumanos c
                LEFT JOIN posts p ON c.id = p.author_id
                GROUP BY c.id
            ),
            max_posts AS (
                SELECT COALESCE(MAX(post_count), 0) AS max_c FROM author_post_counts
            ),
            weighted_authors AS (
                -- Using the aggressive Exponential Weighting (Solution A)
                -- so trailing authors catch up significantly faster
                SELECT
                    apc.author_id,
                    POWER((m.max_c - apc.post_count) + 1, 2) AS weight
                FROM author_post_counts apc
                CROSS JOIN max_posts m
            ),
            random_draws AS (
                SELECT
                    s.slot_id,
                    w.author_id,
                    ROW_NUMBER() OVER (
                        PARTITION BY s.slot_id
                        ORDER BY (-LN(RANDOM()) / w.weight) ASC
                    ) AS ranking
                FROM weighted_authors w
                CROSS JOIN slots s
            )
            SELECT author_id
            FROM random_draws
            WHERE ranking = 1;
        '''

        result = await self.session.execute(sa.text(query), {'slots_count': amount})
        return [row.author_id for row in result]
