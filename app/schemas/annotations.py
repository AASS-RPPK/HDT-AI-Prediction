from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AnnotationRequest(BaseModel):
    image_id: str
    model_name: str = "default"
    parameters: dict[str, Any] | None = None


class AnnotationResponse(BaseModel):
    id: str
    image_id: str
    model_name: str
    state: str
    celery_task_id: str | None = None
    parameters: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnnotationListResponse(BaseModel):
    tasks: list[AnnotationResponse]
    total: int
