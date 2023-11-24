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
        - Clip
        - Dataset
        - SoundEvent
        - Sequence
        - SoundEventAnnotation
        - ClipAnnotations
        - AnnotationState
        - AnnotationTask
        - AnnotationProject
        - PredictedTag
        - SoundEventPrediction
        - ClipPredictions
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
