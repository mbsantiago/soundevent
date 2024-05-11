from pathlib import Path

import pytest

from soundevent.io.aoef.annotation_project import AnnotationProjectAdapter
from soundevent.io.aoef.annotation_set import AnnotationSetAdapter
from soundevent.io.aoef.annotation_task import AnnotationTaskAdapter
from soundevent.io.aoef.clip import ClipAdapter
from soundevent.io.aoef.clip_annotations import ClipAnnotationsAdapter
from soundevent.io.aoef.clip_evaluation import ClipEvaluationAdapter
from soundevent.io.aoef.clip_predictions import ClipPredictionsAdapter
from soundevent.io.aoef.evaluation import EvaluationAdapter
from soundevent.io.aoef.evaluation_set import EvaluationSetAdapter
from soundevent.io.aoef.match import MatchAdapter
from soundevent.io.aoef.model_run import ModelRunAdapter
from soundevent.io.aoef.note import NoteAdapter
from soundevent.io.aoef.prediction_set import PredictionSetAdapter
from soundevent.io.aoef.recording import RecordingAdapter
from soundevent.io.aoef.recording_set import RecordingSetAdapter
from soundevent.io.aoef.sequence import SequenceAdapter
from soundevent.io.aoef.sequence_annotation import SequenceAnnotationAdapter
from soundevent.io.aoef.sequence_prediction import SequencePredictionAdapter
from soundevent.io.aoef.sound_event import SoundEventAdapter
from soundevent.io.aoef.sound_event_annotation import (
    SoundEventAnnotationAdapter,
)
from soundevent.io.aoef.sound_event_prediction import (
    SoundEventPredictionAdapter,
)
from soundevent.io.aoef.tag import TagAdapter
from soundevent.io.aoef.user import UserAdapter


@pytest.fixture
def tag_adapter() -> TagAdapter:
    return TagAdapter()


@pytest.fixture
def user_adapter() -> UserAdapter:
    return UserAdapter()


@pytest.fixture
def note_adapter(user_adapter: UserAdapter) -> NoteAdapter:
    return NoteAdapter(user_adapter)


@pytest.fixture
def recording_adapter(
    tag_adapter: TagAdapter,
    user_adapter: UserAdapter,
    note_adapter: NoteAdapter,
    audio_dir: Path,
) -> RecordingAdapter:
    return RecordingAdapter(
        user_adapter,
        tag_adapter,
        note_adapter,
        audio_dir=audio_dir,
    )


@pytest.fixture
def recording_set_adapter(
    audio_dir: Path,
    user_adapter: UserAdapter,
    tag_adapter: TagAdapter,
    note_adapter: NoteAdapter,
    recording_adapter: RecordingAdapter,
) -> RecordingSetAdapter:
    return RecordingSetAdapter(
        audio_dir=audio_dir,
        user_adapter=user_adapter,
        tag_adapter=tag_adapter,
        note_adapter=note_adapter,
        recording_adapter=recording_adapter,
    )


@pytest.fixture
def sound_event_adapter(
    recording_adapter: RecordingAdapter,
) -> SoundEventAdapter:
    return SoundEventAdapter(recording_adapter)


@pytest.fixture
def clip_adapter(
    recording_adapter: RecordingAdapter,
) -> ClipAdapter:
    return ClipAdapter(recording_adapter)


@pytest.fixture
def sequence_adapter(
    sound_event_adapter: SoundEventAdapter,
) -> SequenceAdapter:
    return SequenceAdapter(
        sound_event_adapter,
    )


@pytest.fixture
def sound_event_annotation_adapter(
    user_adapter: UserAdapter,
    tag_adapter: TagAdapter,
    note_adapter: NoteAdapter,
    sound_event_adapter: SoundEventAdapter,
) -> SoundEventAnnotationAdapter:
    return SoundEventAnnotationAdapter(
        user_adapter,
        tag_adapter,
        note_adapter,
        sound_event_adapter,
    )


@pytest.fixture
def sequence_annotation_adapter(
    user_adapter: UserAdapter,
    tag_adapter: TagAdapter,
    note_adapter: NoteAdapter,
    sequence_adapter: SequenceAdapter,
) -> SequenceAnnotationAdapter:
    return SequenceAnnotationAdapter(
        user_adapter,
        tag_adapter,
        note_adapter,
        sequence_adapter,
    )


@pytest.fixture
def clip_annotations_adapter(
    clip_adapter: ClipAdapter,
    tag_adapter: TagAdapter,
    note_adapter: NoteAdapter,
    sound_event_annotation_adapter: SoundEventAnnotationAdapter,
    sequence_annotation_adapter: SequenceAnnotationAdapter,
) -> ClipAnnotationsAdapter:
    return ClipAnnotationsAdapter(
        clip_adapter,
        tag_adapter,
        note_adapter,
        sound_event_annotation_adapter,
        sequence_annotation_adapter,
    )


@pytest.fixture
def annotation_task_adapter(
    clip_adapter: ClipAdapter,
    user_adapter: UserAdapter,
) -> AnnotationTaskAdapter:
    return AnnotationTaskAdapter(
        clip_adapter=clip_adapter,
        user_adapter=user_adapter,
    )


@pytest.fixture
def annotation_set_adapter(
    audio_dir: Path,
    user_adapter: UserAdapter,
    tag_adapter: TagAdapter,
    note_adapter: NoteAdapter,
    recording_adapter: RecordingAdapter,
    clip_adapter: ClipAdapter,
    sound_event_adapter: SoundEventAdapter,
    sound_event_annotation_adapter: SoundEventAnnotationAdapter,
    clip_annotations_adapter: ClipAnnotationsAdapter,
) -> AnnotationSetAdapter:
    return AnnotationSetAdapter(
        audio_dir=audio_dir,
        user_adapter=user_adapter,
        tag_adapter=tag_adapter,
        note_adapter=note_adapter,
        recording_adapter=recording_adapter,
        clip_adapter=clip_adapter,
        sound_event_adapter=sound_event_adapter,
        sound_event_annotations_adapter=sound_event_annotation_adapter,
        clip_annotation_adapter=clip_annotations_adapter,
    )


@pytest.fixture
def annotation_project_adapter(
    audio_dir: Path,
    user_adapter: UserAdapter,
    tag_adapter: TagAdapter,
    note_adapter: NoteAdapter,
    recording_adapter: RecordingAdapter,
    clip_adapter: ClipAdapter,
    sound_event_adapter: SoundEventAdapter,
    sound_event_annotation_adapter: SoundEventAnnotationAdapter,
    clip_annotations_adapter: ClipAnnotationsAdapter,
    annotation_task_adapter: AnnotationTaskAdapter,
) -> AnnotationProjectAdapter:
    return AnnotationProjectAdapter(
        audio_dir=audio_dir,
        user_adapter=user_adapter,
        tag_adapter=tag_adapter,
        note_adapter=note_adapter,
        recording_adapter=recording_adapter,
        clip_adapter=clip_adapter,
        sound_event_adapter=sound_event_adapter,
        sound_event_annotations_adapter=sound_event_annotation_adapter,
        clip_annotation_adapter=clip_annotations_adapter,
        annotation_task_adapter=annotation_task_adapter,
    )


@pytest.fixture
def evaluation_set_adapter(
    audio_dir: Path,
    user_adapter: UserAdapter,
    tag_adapter: TagAdapter,
    note_adapter: NoteAdapter,
    recording_adapter: RecordingAdapter,
    clip_adapter: ClipAdapter,
    sound_event_adapter: SoundEventAdapter,
    sound_event_annotation_adapter: SoundEventAnnotationAdapter,
    clip_annotations_adapter: ClipAnnotationsAdapter,
) -> EvaluationSetAdapter:
    return EvaluationSetAdapter(
        audio_dir=audio_dir,
        user_adapter=user_adapter,
        tag_adapter=tag_adapter,
        note_adapter=note_adapter,
        recording_adapter=recording_adapter,
        clip_adapter=clip_adapter,
        sound_event_adapter=sound_event_adapter,
        sound_event_annotations_adapter=sound_event_annotation_adapter,
        clip_annotation_adapter=clip_annotations_adapter,
    )


@pytest.fixture
def sound_event_prediction_adapter(
    sound_event_adapter: SoundEventAdapter,
    tag_adapter: TagAdapter,
) -> SoundEventPredictionAdapter:
    return SoundEventPredictionAdapter(
        sound_event_adapter,
        tag_adapter,
    )


@pytest.fixture
def sequence_prediction_adapter(
    sequence_adapter: SequenceAdapter,
    tag_adapter: TagAdapter,
) -> SequencePredictionAdapter:
    return SequencePredictionAdapter(
        sequence_adapter,
        tag_adapter,
    )


@pytest.fixture
def clip_predictions_adapter(
    clip_adapter: ClipAdapter,
    sound_event_prediction_adapter: SoundEventPredictionAdapter,
    tag_adapter: TagAdapter,
    sequence_prediction_adapter: SequencePredictionAdapter,
) -> ClipPredictionsAdapter:
    return ClipPredictionsAdapter(
        clip_adapter,
        sound_event_prediction_adapter,
        tag_adapter,
        sequence_prediction_adapter,
    )


@pytest.fixture
def prediction_set_adapter(
    audio_dir: Path,
    user_adapter: UserAdapter,
    tag_adapter: TagAdapter,
    note_adapter: NoteAdapter,
    recording_adapter: RecordingAdapter,
    clip_adapter: ClipAdapter,
    sound_event_adapter: SoundEventAdapter,
    sound_event_prediction_adapter: SoundEventPredictionAdapter,
    clip_predictions_adapter: ClipPredictionsAdapter,
) -> PredictionSetAdapter:
    return PredictionSetAdapter(
        audio_dir=audio_dir,
        user_adapter=user_adapter,
        tag_adapter=tag_adapter,
        note_adapter=note_adapter,
        recording_adapter=recording_adapter,
        clip_adapter=clip_adapter,
        sound_event_adapter=sound_event_adapter,
        sound_event_prediction_adapter=sound_event_prediction_adapter,
        clip_predictions_adapter=clip_predictions_adapter,
    )


@pytest.fixture
def model_run_adapter(
    audio_dir: Path,
    user_adapter: UserAdapter,
    tag_adapter: TagAdapter,
    note_adapter: NoteAdapter,
    recording_adapter: RecordingAdapter,
    clip_adapter: ClipAdapter,
    sound_event_adapter: SoundEventAdapter,
    sound_event_prediction_adapter: SoundEventPredictionAdapter,
    clip_predictions_adapter: ClipPredictionsAdapter,
) -> ModelRunAdapter:
    return ModelRunAdapter(
        audio_dir=audio_dir,
        user_adapter=user_adapter,
        tag_adapter=tag_adapter,
        note_adapter=note_adapter,
        recording_adapter=recording_adapter,
        clip_adapter=clip_adapter,
        sound_event_adapter=sound_event_adapter,
        sound_event_prediction_adapter=sound_event_prediction_adapter,
        clip_predictions_adapter=clip_predictions_adapter,
    )


@pytest.fixture
def match_adapter(
    sound_event_annotation_adapter: SoundEventAnnotationAdapter,
    sound_event_prediction_adapter: SoundEventPredictionAdapter,
) -> MatchAdapter:
    return MatchAdapter(
        sound_event_annotation_adapter,
        sound_event_prediction_adapter,
    )


@pytest.fixture
def clip_evaluation_adapter(
    clip_annotations_adapter: ClipAnnotationsAdapter,
    clip_predictions_adapter: ClipPredictionsAdapter,
    note_adapter: NoteAdapter,
    match_adapter: MatchAdapter,
) -> ClipEvaluationAdapter:
    return ClipEvaluationAdapter(
        clip_annotations_adapter,
        clip_predictions_adapter,
        note_adapter,
        match_adapter,
    )


@pytest.fixture
def evaluation_adapter(
    audio_dir: Path,
    user_adapter: UserAdapter,
    tag_adapter: TagAdapter,
    note_adapter: NoteAdapter,
    recording_adapter: RecordingAdapter,
    clip_adapter: ClipAdapter,
    sound_event_adapter: SoundEventAdapter,
    sound_event_annotation_adapter: SoundEventAnnotationAdapter,
    clip_annotations_adapter: ClipAnnotationsAdapter,
    sound_event_prediction_adapter: SoundEventPredictionAdapter,
    clip_predictions_adapter: ClipPredictionsAdapter,
    clip_evaluation_adapter: ClipEvaluationAdapter,
    match_adapter: MatchAdapter,
) -> EvaluationAdapter:
    return EvaluationAdapter(
        audio_dir=audio_dir,
        user_adapter=user_adapter,
        tag_adapter=tag_adapter,
        note_adapter=note_adapter,
        recording_adapter=recording_adapter,
        clip_adapter=clip_adapter,
        sound_event_adapter=sound_event_adapter,
        sound_event_annotation_adapter=sound_event_annotation_adapter,
        clip_annotations_adapter=clip_annotations_adapter,
        sound_event_prediction_adapter=sound_event_prediction_adapter,
        clip_predictions_adapter=clip_predictions_adapter,
        clip_evaluation_adapter=clip_evaluation_adapter,
        match_adapter=match_adapter,
    )
