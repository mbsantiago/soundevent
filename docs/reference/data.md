# Data Module

## Basic Models

::: soundevent.data
    options:
        members:
        - User
        - Tag
        - Feature
        - Note
        - Recording
        - Dataset
        - SoundEvent
        - Sequence
        - Clip
        - SoundEventAnnotation
        - SequenceAnnotation
        - ClipAnnotation
        - AnnotationState
        - StatusBadge
        - AnnotationTask
        - AnnotationProject
        - PredictedTag
        - SoundEventPrediction
        - SequencePrediction
        - ClipPrediction
        - ModelRun
        - EvaluationSet
        - Match
        - ClipEvaluation
        - Evaluation

## Geometries

::: soundevent.data.geometries
    options:
        members:
        - TimeStamp
        - TimeInterval
        - Point
        - LineString
        - BoundingBox
        - Polygon
        - MultiPoint
        - MultiLineString
        - MultiPolygon
        - Geometry
