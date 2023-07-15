"""Data classes for working with sound events.

The `soundevent.data` module contains a collection of data classes specifically
designed for working with sound events in the field of bioacoustic research.
These data classes are built using pydantic, a library that offers robust
validation and typing support.

## Purpose and Functionality

The primary objective of the `soundevent.data` module is to provide clearly
defined and standardized objects that facilitate the handling and manipulation
of sound events. These objects are designed to be reusable and serve as
building blocks for constructing complex analysis pipelines and workflows
within the bioacoustic software community.

## Key Features

* Validation: The data classes in this module enforce data validation, ensuring
that the input adheres to the defined structure and constraints. This helps
maintain data integrity and reliability throughout the analysis process.

* Typing Support: The data classes incorporate type annotations, enabling
developers to leverage the benefits of static typing. Clear and consistent
typing promotes code clarity, readability, and facilitates integration with
other libraries and tools.

By utilizing the data classes provided in the `soundevent.data` module,
researchers and developers can work with well-defined and validated objects,
fostering reproducibility and efficient collaboration in bioacoustic research
endeavors.
"""

from soundevent.data.annotation_projects import AnnotationProject
from soundevent.data.annotation_tasks import AnnotationTask
from soundevent.data.annotations import Annotation
from soundevent.data.clips import Clip
from soundevent.data.dataset import Dataset
from soundevent.data.features import Feature
from soundevent.data.geometries import (
    MAX_FREQUENCY,
    BoundingBox,
    Frequency,
    Geometry,
    GeometryType,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
    Time,
    TimeInterval,
    TimeStamp,
)
from soundevent.data.matches import Match
from soundevent.data.model_run import ModelRun
from soundevent.data.notes import Note
from soundevent.data.predicted_sound_events import PredictedSoundEvent
from soundevent.data.predicted_tags import PredictedTag
from soundevent.data.processed_clip import ProcessedClip
from soundevent.data.recordings import Recording
from soundevent.data.sequences import Sequence
from soundevent.data.sound_events import SoundEvent
from soundevent.data.tags import Tag

__all__ = [
    "Annotation",
    "AnnotationProject",
    "AnnotationTask",
    "BoundingBox",
    "Clip",
    "Dataset",
    "Feature",
    "Frequency",
    "Geometry",
    "GeometryType",
    "LineString",
    "MAX_FREQUENCY",
    "Match",
    "ModelRun",
    "MultiLineString",
    "MultiPoint",
    "MultiPolygon",
    "Note",
    "Point",
    "Polygon",
    "PredictedSoundEvent",
    "PredictedTag",
    "ProcessedClip",
    "Recording",
    "Sequence",
    "SoundEvent",
    "Tag",
    "Time",
    "TimeInterval",
    "TimeStamp",
]
