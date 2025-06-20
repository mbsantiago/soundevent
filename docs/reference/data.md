# Data Module

## Basic Models

::: soundevent.data
    options:
        members:
        - User
        - Term
        - Tag
        - Feature
        - Note
        - Recording
        - RecordingSet
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
        - AnnotationSet
        - AnnotationProject
        - PredictedTag
        - SoundEventPrediction
        - SequencePrediction
        - ClipPrediction
        - PredictionSet
        - ModelRun
        - EvaluationSet
        - Match
        - ClipEvaluation
        - Evaluation
        - find_tag
        - find_tag_value
        - find_feature
        - find_feature_value

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


## Other

::: soundevent.data.PathLike
    options:
        heading_level: 3
