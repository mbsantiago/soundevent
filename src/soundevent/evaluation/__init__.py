"""Evaluation functions."""

from soundevent.evaluation.affinity import compute_affinity
from soundevent.evaluation.encoding import (
    classification_encoding,
    create_tag_encoder,
    multilabel_encoding,
    prediction_encoding,
)
from soundevent.evaluation.match import (
    Match,
    match_detections_and_gts,
    match_geometries,
)
from soundevent.evaluation.tasks import (
    clip_classification,
    clip_multilabel_classification,
    sound_event_classification,
    sound_event_detection,
)

__all__ = [
    "Match",
    "classification_encoding",
    "clip_classification",
    "clip_multilabel_classification",
    "compute_affinity",
    "create_tag_encoder",
    "match_detections_and_gts",
    "match_geometries",
    "multilabel_encoding",
    "prediction_encoding",
    "sound_event_classification",
    "sound_event_detection",
]
