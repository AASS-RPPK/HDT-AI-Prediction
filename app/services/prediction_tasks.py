from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PredictionState, PredictionTask
from app.schemas.annotations import AnnotationRequest
from app.worker.tasks import run_prediction


def create_prediction_task(db: Session, request: AnnotationRequest) -> PredictionTask:
    task = PredictionTask(
        image_id=request.image_id,
        model_name=request.model_name,
        state=PredictionState.PENDING.value,
        parameters=request.parameters,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    celery_result = run_prediction.delay(
        task_id=task.id,
        image_id=request.image_id,
        model_name=request.model_name,
        parameters=request.parameters,
    )

    task.celery_task_id = celery_result.id
    db.commit()
    db.refresh(task)

    return task


def get_prediction_task(db: Session, task_id: str) -> PredictionTask | None:
    stmt = select(PredictionTask).where(PredictionTask.id == task_id).limit(1)
    return db.execute(stmt).scalars().first()


def list_prediction_tasks(
    db: Session,
    *,
    image_id: str | None = None,
    state: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[PredictionTask], int]:
    stmt = select(PredictionTask)
    if image_id:
        stmt = stmt.where(PredictionTask.image_id == image_id)
    if state:
        stmt = stmt.where(PredictionTask.state == state)

    count_stmt = stmt
    total = db.execute(
        count_stmt.with_only_columns(PredictionTask.id)
    ).all().__len__()

    stmt = stmt.order_by(PredictionTask.created_at.desc()).limit(limit).offset(offset)
    tasks = list(db.execute(stmt).scalars().all())
    return tasks, total
