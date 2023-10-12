from typing import Iterable, Tuple

from soundevent import data


def iterate_over_valid_examples(
    model_run: data.ModelRun,
    evaluation_set: data.EvaluationSet,
) -> Iterable[Tuple[data.EvaluationExample, data.ProcessedClip]]:
    evaluation_set_clips = {
        example.clip.uuid: example for example in evaluation_set.examples
    }

    for processed_clip in model_run.clips:
        if processed_clip.clip.uuid in evaluation_set_clips:
            evaluation_example = evaluation_set_clips[processed_clip.clip.uuid]
            yield evaluation_example, processed_clip
