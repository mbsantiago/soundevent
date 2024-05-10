from typing import Iterable, Sequence, Tuple

from soundevent import data


def iterate_over_valid_clips(
    clip_predictions: Sequence[data.ClipPrediction],
    clip_annotations: Sequence[data.ClipAnnotation],
) -> Iterable[Tuple[data.ClipAnnotation, data.ClipPrediction]]:
    annotated_clips = {
        example.clip.uuid: example for example in clip_annotations
    }

    for predictions in clip_predictions:
        if predictions.clip.uuid in annotated_clips:
            annotations = annotated_clips[predictions.clip.uuid]
            yield annotations, predictions
