import enum

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped

from app.common.database import Base


# 1. Define your strict two-value integer states
class JobPriority(enum.IntEnum):
    STANDARD = 0
    HIGH = 1


class JobModel(Base):
    __tablename__ = "jobs"

    priority: Mapped[JobPriority] = mapped_column(
        sa.Enum(JobPriority, values_callable=lambda x: [item.value for item in x]),
        default=JobPriority.STANDARD,
        nullable=False,
        index=True  # Keeps sorting queries fast when ordering your queue
    )
