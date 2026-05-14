"""
Kafka consumer for HDT AI Prediction.

Subscribes to aiPrediction.retrieve events produced by Active Learning,
simulates annotation retrieval from the model, and publishes the result
to model.train.deploy for Active Learning to act on.

Message format in:
  {"taskId": str, "feedbackId": str, "caseId": str, "slideId": str, "log": str}

Message format out:
  {"taskId": str, "predictionId": str, "caseId": str, "log": str}
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

TOPIC_AI_PREDICTION_RETRIEVE = "aiPrediction.retrieve"
TOPIC_MODEL_TRAIN_DEPLOY     = "model.train.deploy"

log = logging.getLogger("hdt.ai_prediction.kafka")


async def run_prediction_consumer() -> None:
    """Long-running coroutine: consume aiPrediction.retrieve, produce model.train.deploy."""
    producer: AIOKafkaProducer | None = None
    for attempt in range(1, 31):
        try:
            producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP)
            await producer.start()
            log.info("Kafka producer connected (attempt %d).", attempt)
            break
        except Exception as exc:
            log.warning("Kafka not ready (attempt %d/30): %s", attempt, exc)
            producer = None
            await asyncio.sleep(5)
    else:
        log.error("Could not connect to Kafka — prediction consumer not started.")
        return

    consumer = AIOKafkaConsumer(
        TOPIC_AI_PREDICTION_RETRIEVE,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id="ai-prediction-retrieve",
        auto_offset_reset="latest",
    )
    await consumer.start()
    log.info("Prediction Kafka consumer ready on topic '%s'.", TOPIC_AI_PREDICTION_RETRIEVE)

    try:
        async for msg in consumer:
            data: dict = json.loads(msg.value.decode())
            task_id    = data.get("taskId", "")
            case_id    = data.get("caseId", "")

            log.info("[kafka] aiPrediction.retrieve taskId=%s caseId=%s", task_id, case_id)

            # Simulate annotation prediction retrieval (no-op)
            prediction_id = str(uuid.uuid4())

            response_payload = json.dumps({
                "taskId":       task_id,
                "predictionId": prediction_id,
                "caseId":       case_id,
                "log":          "AI Prediction retrieved (simulated). Triggering model train+deploy.",
            }).encode()
            await producer.send_and_wait(TOPIC_MODEL_TRAIN_DEPLOY, response_payload)
            log.info("[kafka] model.train.deploy produced for taskId=%s", task_id)
    finally:
        await consumer.stop()
        await producer.stop()
