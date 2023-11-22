from typing import Iterable, Tuple

from soundevent import data


def iterate_over_valid_clips(
    prediction_set: data.PredictionSet,
    annotation_set: data.AnnotationSet,
) -> Iterable[Tuple[data.ClipAnnotations, data.ClipPredictions]]:
    annotation_set_clips = {
        example.clip.uuid: example
        for example in annotation_set.clip_annotations
    }

    for clip_predictions in prediction_set.clip_predictions:
        if clip_predictions.clip.uuid in annotation_set_clips:
            clip_annotations = annotation_set_clips[clip_predictions.clip.uuid]
            yield clip_annotations, clip_predictions
