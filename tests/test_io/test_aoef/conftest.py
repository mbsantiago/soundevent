from pathlib import Path
from typing import Callable, List

import pytest

from soundevent import data
from soundevent.io.aoef.annotation_set import AnnotationSetAdapter
from soundevent.io.aoef.annotation_task import AnnotationTaskAdapter
from soundevent.io.aoef.clip import ClipAdapter
from soundevent.io.aoef.clip_annotations import ClipAnnotationsAdapter
from soundevent.io.aoef.note import NoteAdapter
from soundevent.io.aoef.recording import RecordingAdapter
from soundevent.io.aoef.sound_event import SoundEventAdapter
from soundevent.io.aoef.sound_event_annotation import SoundEventAnnotationAdapter
from soundevent.io.aoef.tag import TagAdapter
from soundevent.io.aoef.user import UserAdapter
from soundevent.io.aoef.annotation_project import AnnotationProjectAdapter


@pytest.fixture
def tags(random_tags: Callable[[int], List[data.Tag]]) -> List[data.Tag]:
    return random_tags(3)


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
def clip_adapter(
    recording_adapter: RecordingAdapter,
) -> ClipAdapter:
    return ClipAdapter(recording_adapter)


@pytest.fixture
def sound_event_adapter() -> SoundEventAdapter:
    return SoundEventAdapter()


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
def clip_annotations(
    tags: List[data.Tag],
    clip: data.Clip,
    note: data.Note,
    sound_event_annotation: data.SoundEventAnnotation,
):
    return data.ClipAnnotations(
        clip=clip,
        notes=[note],
        tags=tags[:2],
        annotations=[sound_event_annotation],
    )


@pytest.fixture
def clip_annotations_adapter(
    clip_adapter: ClipAdapter,
    tag_adapter: TagAdapter,
    note_adapter: NoteAdapter,
    sound_event_annotation_adapter: SoundEventAnnotationAdapter,
) -> ClipAnnotationsAdapter:
    return ClipAnnotationsAdapter(
        clip_adapter,
        tag_adapter,
        note_adapter,
        sound_event_annotation_adapter,
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
def annotation_set(clip_annotations: data.ClipAnnotations):
    return data.AnnotationSet(clip_annotations=[clip_annotations])


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
def annotation_project(
    annotation_task: data.AnnotationTask,
    clip_annotations: data.ClipAnnotations,
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
