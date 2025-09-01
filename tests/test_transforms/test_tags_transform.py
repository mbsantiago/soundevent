from pathlib import Path
from typing import Optional, Sequence

from soundevent import data
from soundevent.transforms import TagsTransform


def test_tags_transform_with_sequence_fn_remove_tag():
    # Given
    tags = [data.Tag(key="a", value="1"), data.Tag(key="b", value="2")]  # type: ignore
    recording = data.Recording(
        path=Path("rec.wav"),
        duration=1,
        channels=1,
        samplerate=16000,
        tags=tags,
    )

    def remove_a(tags: Sequence[data.Tag]) -> Sequence[data.Tag]:
        return [tag for tag in tags if tag.key != "a"]

    transformer = TagsTransform(transform=remove_a)

    # When
    transformed_recording = transformer.transform_recording(recording)

    # Then
    assert len(transformed_recording.tags) == 1
    assert transformed_recording.tags[0].key == "b"


def test_tags_transform_from_tag_transform_modify_tag():
    # Given
    tags = [data.Tag(key="a", value="1"), data.Tag(key="b", value="2")]  # type: ignore
    recording = data.Recording(
        path=Path("rec.wav"),
        duration=1,
        channels=1,
        samplerate=16000,
        tags=tags,
    )

    def change_a_value(tag: data.Tag) -> data.Tag:
        if tag.key == "a":
            return tag.model_copy(update={"value": "99"})
        return tag

    transformer = TagsTransform.from_tag_transform(transform=change_a_value)

    # When
    transformed_recording = transformer.transform_recording(recording)

    # Then
    assert len(transformed_recording.tags) == 2
    assert data.Tag(key="a", value="99") in transformed_recording.tags  # type: ignore
    assert data.Tag(key="b", value="2") in transformed_recording.tags  # type: ignore


def test_tags_transform_from_tag_transform_remove_tag():
    # Given
    tags = [data.Tag(key="a", value="1"), data.Tag(key="b", value="2")]  # type: ignore
    recording = data.Recording(
        path=Path("rec.wav"),
        duration=1,
        channels=1,
        samplerate=16000,
        tags=tags,
    )

    def remove_a(tag: data.Tag) -> Optional[data.Tag]:
        if tag.key == "a":
            return None
        return tag

    transformer = TagsTransform.from_tag_transform(transform=remove_a)

    # When
    transformed_recording = transformer.transform_recording(recording)

    # Then
    assert len(transformed_recording.tags) == 1
    assert transformed_recording.tags[0].key == "b"


def test_tags_transform_is_applied_to_clip_annotation_tags():
    # Given
    annotation = data.ClipAnnotation(
        clip=data.Clip(
            recording=data.Recording(
                path=Path("rec.wav"),
                duration=1,
                channels=1,
                samplerate=16000,
            ),
            start_time=0,
            end_time=1,
        ),
        tags=[data.Tag(key="a", value="c"), data.Tag(key="b", value="d")],  # type: ignore
    )

    def remove_a(tag: data.Tag) -> Optional[data.Tag]:
        return None if tag.key == "a" else tag

    transformer = TagsTransform.from_tag_transform(transform=remove_a)

    # When
    transformed_annotation = transformer.transform_clip_annotation(annotation)

    # Then
    assert len(transformed_annotation.tags) == 1
    assert transformed_annotation.tags[0].key == "b"
