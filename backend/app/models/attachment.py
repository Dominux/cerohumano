import enum
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.common.database import Base
from app.models.post import PostModel
from app.models.cerohumano import CeroHumanoModel


# 1. Define attachment types
class AttachmentType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"


class AttachmentModel(Base):
    __tablename__ = "attachments"

    # Explicitly stores what kind of asset this is (image, video, etc.)
    file_type: Mapped[AttachmentType] = mapped_column(
        sa.Enum(AttachmentType),
        nullable=False,
        default=AttachmentType.IMAGE,
    )

    # Optional metadata (e.g., duration for videos, dimensions for all)
    # Stored as a JSON object to support flexible, asset-specific attributes
    meta_data: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)

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

    # Optional Link to Post (nullable=True allows use in other scenarios)
    post_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("posts.id", ondelete="SET NULL"),
        nullable=True
    )
    post: Mapped["PostModel | None"] = relationship(
        "PostModel",
        foreign_keys=[post_id],
    )
