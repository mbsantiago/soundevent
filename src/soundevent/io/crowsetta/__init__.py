"""Crowsetta Module.

This module provides a set of functions to facilitate the export and import of
data in the soundevent format to and from the Crowsetta format.
"""

from soundevent.io.crowsetta.annotation import (
    annotation_from_clip_annotation,
    annotation_to_clip_annotation,
)
from soundevent.io.crowsetta.bbox import (
    bbox_from_annotation,
    bbox_to_annotation,
)
from soundevent.io.crowsetta.labels import (
    label_from_tag,
    label_from_tags,
    label_to_tags,
)
from soundevent.io.crowsetta.segment import (
    segment_from_annotation,
    segment_to_annotation,
)
from soundevent.io.crowsetta.sequence import (
    sequence_from_annotations,
    sequence_to_annotations,
)

__all__ = [
    "annotation_from_clip_annotation",
    "annotation_to_clip_annotation",
    "bbox_from_annotation",
    "bbox_to_annotation",
    "label_from_tag",
    "label_from_tags",
    "label_to_tags",
    "segment_from_annotation",
    "segment_to_annotation",
    "sequence_from_annotations",
    "sequence_to_annotations",
]
