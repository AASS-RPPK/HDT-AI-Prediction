from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.annotations import (
    AnnotationListResponse,
    AnnotationRequest,
    AnnotationResponse,
)
from app.services.deterministic import deterministic_result
from app.services.prediction_tasks import create_prediction_task, list_prediction_tasks

router = APIRouter(prefix="/model", tags=["model"])


@router.post("/annotations", response_model=AnnotationResponse, status_code=202)
def post_annotations(
    request: AnnotationRequest,
    db: Session = Depends(get_db),
) -> AnnotationResponse:
    """Submit an AI model prediction task for the given image.

    The task is queued via Celery and processed asynchronously.
    Returns immediately with the task record (state=PENDING).
    """
    task = create_prediction_task(db, request)
    return AnnotationResponse.model_validate(task)


@router.get("/annotations", response_model=AnnotationListResponse)
def get_annotations(
    image_id: str | None = Query(default=None, description="Filter by image ID"),
    state: str | None = Query(default=None, description="Filter by task state"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> AnnotationListResponse:
    """Retrieve prediction annotation results.

    Supports filtering by image_id and/or state, with pagination.
    """
    tasks, total = list_prediction_tasks(
        db, image_id=image_id, state=state, limit=limit, offset=offset
    )
    # Backfill historical empty results so callers always receive annotations.
    changed = False
    for task in tasks:
        result = task.result or {}
        annotations = result.get("annotations", [])
        if task.state == "COMPLETED" and isinstance(annotations, list) and len(annotations) == 0:
            task.result = deterministic_result(image_id=task.image_id, model_name=task.model_name)
            changed = True
    if changed:
        db.commit()
        for task in tasks:
            db.refresh(task)

    return AnnotationListResponse(
        tasks=[AnnotationResponse.model_validate(t) for t in tasks],
        total=total,
    )
