from __future__ import annotations

import hashlib
from typing import Any


def _fraction_from_hex(chunk: str) -> float:
    return int(chunk, 16) / float(16 ** len(chunk))


def deterministic_result(image_id: str, model_name: str) -> dict[str, Any]:
    """Generate stable mock annotations for the same image/model pair."""
    seed = hashlib.sha256(f"{image_id}|{model_name}".encode("utf-8")).hexdigest()
    labels = ["Tumor region", "Inflammation", "Stroma", "Necrosis"]

    annotations: list[dict[str, Any]] = []
    for i in range(3):
        base = i * 10
        fx = _fraction_from_hex(seed[base : base + 4])
        fy = _fraction_from_hex(seed[base + 4 : base + 8])
        fw = _fraction_from_hex(seed[base + 8 : base + 10])
        fh = _fraction_from_hex(seed[base + 10 : base + 12])

        x = int(400 + fx * 7600)
        y = int(400 + fy * 7600)
        w = int(500 + fw * 1200)
        h = int(500 + fh * 1200)
        conf = round(0.65 + (_fraction_from_hex(seed[base + 12 : base + 14]) * 0.3), 3)
        label = labels[int(_fraction_from_hex(seed[base + 14 : base + 16]) * len(labels)) % len(labels)]

        annotations.append(
            {
                "id": f"ai-{seed[:12]}-{i + 1}",
                "type": "Annotation",
                "body": [
                    {"type": "TextualBody", "purpose": "tagging", "value": label},
                    {"type": "TextualBody", "purpose": "commenting", "value": f"confidence={conf}"},
                ],
                "target": {
                    "selector": {
                        "type": "FragmentSelector",
                        "conformsTo": "http://www.w3.org/TR/media-frags/",
                        "value": f"xywh=pixel:{x},{y},{w},{h}",
                    }
                },
            }
        )

    return {
        "annotations": annotations,
        "model_name": model_name,
        "image_id": image_id,
        "deterministic": True,
    }

