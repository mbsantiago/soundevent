import datetime
from pathlib import Path
from typing import Callable, List

import pytest

from tests.conftest import get_random_string

from soundevent import data


@pytest.fixture
def random_tags():
    """Generate a random list of tags for testing."""

    def factory(n=10):
        return [
            data.Tag(
                term=data.term_from_key(get_random_string(10)),
                value=get_random_string(10),
            )
            for _ in range(n)
        ]

    return factory


@pytest.fixture
def tag(random_tags: Callable[[int], List[data.Tag]]) -> data.Tag:
    return random_tags(1)[0]


@pytest.fixture
def tags(random_tags: Callable[[int], List[data.Tag]]) -> List[data.Tag]:
    return random_tags(3)


@pytest.fixture
def recording(
    random_wav: Callable[[], Path],
    user: data.User,
    tags: List[data.Tag],
    note: data.Note,
) -> data.Recording:
    path = random_wav()
    return data.Recording.from_file(
        path,
        date=datetime.date(2020, 1, 1),
        time=datetime.time(12, 0, 0),
        latitude=1.0,
        longitude=2.0,
        owners=[user],
        rights="CC BY 4.0",
        tags=tags,
        notes=[note],
        features=[
            data.Feature(
                term=data.term_from_key("MaxAmp"),
                value=23.3,
            ),
        ],
    )


@pytest.fixture
def time_expanded_recording(
    random_wav: Callable[[], Path],
    user: data.User,
    tags: List[data.Tag],
    note: data.Note,
) -> data.Recording:
    path = random_wav()
    return data.Recording.from_file(
        path,
        date=datetime.date(2020, 1, 1),
        time=datetime.time(12, 0, 0),
        time_expansion=10,
        latitude=1.0,
        longitude=2.0,
        owners=[user],
        rights="CC BY 4.0",
        tags=tags,
        notes=[note],
        features=[
            data.Feature(term=data.term_from_key("MaxAmp"), value=23.3),
        ],
    )


@pytest.fixture
def recording_set(recording: data.Recording) -> data.RecordingSet:
    return data.RecordingSet(recordings=[recording])


@pytest.fixture
def dataset(
    recording: data.Recording,
) -> data.Dataset:
    return data.Dataset(
        name="Test Dataset",
        description="Test Dataset Description",
        recordings=[recording],
    )


@pytest.fixture
def sequence(
    sound_event: data.SoundEvent,
) -> data.Sequence:
    return data.Sequence(
        uuid=sound_event.uuid,
        sound_events=[sound_event],
        features=[
            data.Feature(term=data.term_from_key("duration"), value=23.3),
        ],
    )


@pytest.fixture
def clip(
    recording: data.Recording,
) -> data.Clip:
    return data.Clip(
        recording=recording,
        start_time=0.0,
        end_time=1.0,
        features=[
            data.Feature(term=data.term_from_key("MaxAmp"), value=23.3),
            data.Feature(term=data.term_from_key("SNR"), value=8),
        ],
    )


@pytest.fixture
def sound_event_annotation(
    tags: List[data.Tag],
    sound_event: data.SoundEvent,
    note: data.Note,
    user: data.User,
):
    return data.SoundEventAnnotation(
        sound_event=sound_event,
        notes=[note],
        created_by=user,
        tags=tags,
    )


@pytest.fixture
def sequence_annotation(
    tags: List[data.Tag],
    sequence: data.Sequence,
    note: data.Note,
    user: data.User,
):
    return data.SequenceAnnotation(
        sequence=sequence,
        notes=[note],
        created_by=user,
        tags=tags,
    )


@pytest.fixture
def clip_annotations(
    tags: List[data.Tag],
    clip: data.Clip,
    note: data.Note,
    sound_event_annotation: data.SoundEventAnnotation,
    sequence_annotation: data.SequenceAnnotation,
):
    return data.ClipAnnotation(
        clip=clip,
        notes=[note],
        tags=tags[:2],
        sound_events=[sound_event_annotation],
        sequences=[sequence_annotation],
    )


@pytest.fixture
def annotation_task(
    clip: data.Clip,
    user: data.User,
):
    return data.AnnotationTask(
        clip=clip,
        status_badges=[
            data.StatusBadge(
                state=data.AnnotationState.completed,
                owner=user,
            )
        ],
    )


@pytest.fixture
def annotation_set(clip_annotations: data.ClipAnnotation):
    return data.AnnotationSet(clip_annotations=[clip_annotations])


@pytest.fixture
def annotation_project(
    annotation_task: data.AnnotationTask,
    clip_annotations: data.ClipAnnotation,
    tags: List[data.Tag],
):
    return data.AnnotationProject(
        name="Test Project",
        description="Test Project Description",
        annotation_tags=tags,
        clip_annotations=[clip_annotations],
        tasks=[annotation_task],
    )


@pytest.fixture
def evaluation_set(
    clip_annotations: data.ClipAnnotation,
    tags: List[data.Tag],
):
    return data.EvaluationSet(
        clip_annotations=[clip_annotations],
        name="Test Evaluation Set",
        description="Test Evaluation Set Description",
        evaluation_tags=tags,
    )


@pytest.fixture
def predicted_tags(tags: List[data.Tag]) -> List[data.PredictedTag]:
    return [
        data.PredictedTag(
            tag=tags[0],
            score=0.5,
        ),
        data.PredictedTag(
            tag=tags[1],
            score=0.3,
        ),
        data.PredictedTag(
            tag=tags[2],
            score=0.7,
        ),
    ]


@pytest.fixture
def sound_event_prediction(
    sound_event: data.SoundEvent,
    predicted_tags: List[data.PredictedTag],
):
    return data.SoundEventPrediction(
        sound_event=sound_event,
        score=0.7,
        tags=predicted_tags,
    )


@pytest.fixture
def sequence_prediction(
    sequence: data.Sequence,
    predicted_tags: List[data.PredictedTag],
):
    return data.SequencePrediction(
        sequence=sequence,
        score=0.7,
        tags=predicted_tags,
    )


@pytest.fixture
def clip_predictions(
    clip: data.Clip,
    sound_event_prediction: data.SoundEventPrediction,
    predicted_tags: List[data.PredictedTag],
    sequence_prediction: data.SequencePrediction,
):
    return data.ClipPrediction(
        clip=clip,
        sound_events=[sound_event_prediction],
        tags=predicted_tags[1:],
        features=[
            data.Feature(term=data.term_from_key("VGGish1"), value=23.3),
            data.Feature(term=data.term_from_key("VGGish2"), value=-32.7),
        ],
        sequences=[sequence_prediction],
    )


@pytest.fixture
def prediction_set(
    clip_predictions: data.ClipPrediction,
):
    return data.PredictionSet(
        clip_predictions=[clip_predictions],
    )


@pytest.fixture
def model_run(
    clip_predictions: data.ClipPrediction,
) -> data.ModelRun:
    return data.ModelRun(
        name="Test Model Run",
        description="Test Model Run Description",
        clip_predictions=[clip_predictions],
        version="1.0.0",
    )


@pytest.fixture
def match(
    sound_event_annotation: data.SoundEventAnnotation,
    sound_event_prediction: data.SoundEventPrediction,
):
    return data.Match(
        target=sound_event_annotation,
        source=sound_event_prediction,
        affinity=0.7,
        score=0.4,
        metrics=[
            data.Feature(
                term=data.term_from_key("accuracy"),
                value=0.5,
            ),
        ],
    )


@pytest.fixture
def clip_evaluation(
    clip_annotations: data.ClipAnnotation,
    clip_predictions: data.ClipPrediction,
    match: data.Match,
) -> data.ClipEvaluation:
    return data.ClipEvaluation(
        annotations=clip_annotations,
        predictions=clip_predictions,
        matches=[match],
        metrics=[
            data.Feature(
                term=data.term_from_key("accuracy"),
                value=0.5,
            ),
            data.Feature(
                term=data.term_from_key("f1_score"),
                value=0.5,
            ),
        ],
        score=0.5,
    )


@pytest.fixture
def evaluation(
    clip_evaluation: data.ClipEvaluation,
) -> data.Evaluation:
    return data.Evaluation(
        evaluation_task="Classification",
        metrics=[
            data.Feature(
                term=data.term_from_key("accuracy"),
                value=0.5,
            ),
            data.Feature(
                term=data.term_from_key("f1_score"),
                value=0.5,
            ),
        ],
        clip_evaluations=[
            clip_evaluation,
        ],
        score=0.5,
    )
