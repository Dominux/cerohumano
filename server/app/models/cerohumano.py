import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped

from app.common.database import Base


class CeroHumanoModel(Base):
    __tablename__ = "cerohumano"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    trigger_word: Mapped[str] = mapped_column(nullable=False, unique=True)
    lora_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    cup_enlarge_max: Mapped[float] = mapped_column(
        sa.CheckConstraint("cup_enlarge_max >= 0.0 AND cup_enlarge_max <= 4.0"),
        nullable=False,
        default=0.3,
    )
    # pfp
