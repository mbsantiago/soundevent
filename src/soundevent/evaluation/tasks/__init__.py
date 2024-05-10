from soundevent.evaluation.tasks.clip_classification import clip_classification
from soundevent.evaluation.tasks.clip_multilabel_classification import (
    clip_multilabel_classification,
)
from soundevent.evaluation.tasks.sound_event_classification import (
    sound_event_classification,
)
from soundevent.evaluation.tasks.sound_event_detection import (
    sound_event_detection,
)

__all__ = [
    "clip_classification",
    "clip_multilabel_classification",
    "sound_event_classification",
    "sound_event_detection",
]
