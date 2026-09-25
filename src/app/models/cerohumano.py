import enum
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.common.database import Base


class CeroHumanoCupDescription(enum.IntEnum):
    BIG = enum.auto()
    LARGE = enum.auto()
    HUGE = enum.auto()
    ENORMOUS = enum.auto()
    MASSIVE = enum.auto()
    GIGANTIC = enum.auto()


class CeroHumanoModel(Base):
    __tablename__ = "cerohumanos"

    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)

    trigger_word: Mapped[str] = mapped_column(nullable=False, unique=True)
    lora_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    min_cup: Mapped[CeroHumanoCupDescription] = mapped_column()

    profile_picture_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("attachments.id", ondelete="SET NULL", use_alter=True),
        nullable=True
    )

    profile_picture: Mapped["AttachmentModel | None"] = relationship(
        "AttachmentModel",
        foreign_keys=[profile_picture_id],
    )
