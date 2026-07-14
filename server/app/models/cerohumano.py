import uuid

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.common.database import Base
from app.models.attachment import AttachmentModel


class CeroHumanoModel(Base):
    __tablename__ = "cerohumanos"

    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)

    trigger_word: Mapped[str] = mapped_column(nullable=False, unique=True)
    lora_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    cup_enlarge_max: Mapped[int] = mapped_column(
        sa.CheckConstraint("cup_enlarge_max >= 0 AND cup_enlarge_max <= 10"),
        nullable=False,
        default=0,
    )

    profile_picture_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("attachments.id", ondelete="SET NULL"),
        nullable=True
    )

    profile_picture: Mapped["AttachmentModel | None"] = relationship(
        "AttachmentModel",
        foreign_keys=[profile_picture_id],
        back_populates="profile_users"
    )
