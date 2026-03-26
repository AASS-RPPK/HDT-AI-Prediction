from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PredictionState(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PredictionTask(Base):
    __tablename__ = "prediction_tasks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    image_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(Text, nullable=False)

    state: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Input parameters sent to the model.
    parameters: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    # Prediction result annotations returned by the model.
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
