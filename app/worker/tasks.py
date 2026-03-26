from __future__ import annotations

import logging
from typing import Any

from app.core.celery_app import celery_app
from app.db.models import PredictionState
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="run_prediction")
def run_prediction(
    self,
    task_id: str,
    image_id: str,
    model_name: str,
    parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute AI model inference for the given image and return annotations."""
    from app.db.models import PredictionTask

    db = SessionLocal()
    try:
        task = db.query(PredictionTask).filter(PredictionTask.id == task_id).first()
        if not task:
            raise LookupError(f"PredictionTask {task_id} not found")

        task.state = PredictionState.PROCESSING.value
        db.commit()

        # ------------------------------------------------------------------
        # TODO: Replace the placeholder below with actual model inference.
        #
        # Example integration:
        #   from app.services.model_runner import predict
        #   annotations = predict(image_id, model_name, parameters)
        #
        # The result should be a dict with an "annotations" key containing
        # the list of predicted annotation objects.
        # ------------------------------------------------------------------
        annotations: dict[str, Any] = {
            "annotations": [],
            "model_name": model_name,
            "image_id": image_id,
        }

        task.state = PredictionState.COMPLETED.value
        task.result = annotations
        db.commit()

        logger.info("Prediction %s completed for image %s", task_id, image_id)
        return annotations

    except Exception as exc:
        db.rollback()
        task = db.query(PredictionTask).filter(PredictionTask.id == task_id).first()
        if task:
            task.state = PredictionState.FAILED.value
            task.error = str(exc)
            db.commit()
        logger.exception("Prediction %s failed: %s", task_id, exc)
        raise
    finally:
        db.close()
