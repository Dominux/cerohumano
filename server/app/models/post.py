import uuid

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.common.database import Base
from app.models.cerohumano import CeroHumanoModel


class PostModel(Base):
    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)

    author_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("cerohumanos.id", ondelete="CASCADE"),
        nullable=False
    )

    # 2. Relationship object to access the user data directly via post.author
    author: Mapped["CeroHumanoModel"] = relationship(
        "CeroHumanoModel",
        foreign_keys=[author_id],
    )
