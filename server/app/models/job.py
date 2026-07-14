import enum
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.common.database import Base
from app.models.cerohumano import CeroHumanoModel


# 1. Define your strict two-value integer states
class JobPriority(enum.IntEnum):
    STANDARD = 0
    HIGH = 1


class JobStatus(str, enum.Enum):
    PENDING = "pending"       # Waiting in the queue
    PROCESSING = "processing" # Actively executing right now
    DONE = "done"         # Errored out but keeping for history/retries


class JobType(str, enum.Enum):
    POST = 'post'
    POST_IMAGE_REGEN = 'post_image_regen'


class JobModel(Base):
    __tablename__ = "jobs"

    job_type: Mapped[JobType] = mapped_column(
        sa.Enum(JobType),
        default=JobType.POST,
        nullable=False,
    )

    json_params: Mapped[dict] = mapped_column(
        sa.JSON,                # Explicitly pass the JSON type specifier
        nullable=False,
        default=dict,           # Automatically initializes as {} if empty
        server_default=sa.text("'{}'::jsonb")
    )

    priority: Mapped[JobPriority] = mapped_column(
        sa.Enum(JobPriority),
        default=JobPriority.STANDARD,
        nullable=False,
        index=True  # Keeps sorting queries fast when ordering your queue
    )

    status: Mapped[JobStatus] = mapped_column(
        sa.Enum(JobStatus),
        default=JobStatus.PENDING,
        nullable=False,
        index=True
    )

    cerohumano_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("cerohumanos.id", ondelete="CASCADE"),
        nullable=False
    )

    # 2. Relationship object to access the user data
    cerohumano: Mapped["CeroHumanoModel"] = relationship(
        back_populates="jobs"
    )
