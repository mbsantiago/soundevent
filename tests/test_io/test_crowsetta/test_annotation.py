"""Test suite for the soundevent.io.crowsetta.annotation module."""

import datetime
from pathlib import Path

import crowsetta
import pytest

import soundevent.io.crowsetta as crowsetta_io
from soundevent import data
from soundevent.io.crowsetta.segment import create_crowsetta_segment


@pytest.fixture
def clip_annotation(recording: data.Recording) -> data.ClipAnnotation:
    return data.ClipAnnotation(
        clip=data.Clip(
            recording=recording,
            start_time=0.0,
            end_time=1.0,
        ),
        tags=[
            data.Tag(key="animal", value="dog"),
        ],
        sound_events=[
            data.SoundEventAnnotation(
                sound_event=data.SoundEvent(
                    recording=recording,
                    geometry=data.TimeInterval(coordinates=[0.5, 1.5]),
                    features=[data.Feature(name="test", value=1.0)],
                ),
                tags=[data.Tag(key="animal", value="dog")],
                notes=[data.Note(message="random note")],
            ),
            data.SoundEventAnnotation(
                sound_event=data.SoundEvent(
                    recording=recording,
                    geometry=data.BoundingBox(
                        coordinates=[0.5, 0.5, 1.5, 1.5]
                    ),
                    features=[data.Feature(name="test", value=1.0)],
                ),
                tags=[data.Tag(key="animal", value="cat")],
                notes=[data.Note(message="random note")],
            ),
            data.SoundEventAnnotation(
                sound_event=data.SoundEvent(
                    recording=recording,
                    geometry=data.LineString(
                        coordinates=[[0.5, 0.5], [1.5, 1.5]]
                    ),
                    features=[data.Feature(name="test", value=1.0)],
                ),
                tags=[data.Tag(key="animal", value="cat")],
                notes=[data.Note(message="random note")],
            ),
        ],
        notes=[data.Note(message="random note")],
    )


@pytest.fixture
def sequence_annotation(
    tmp_path: Path,
    recording: data.Recording,
) -> crowsetta.Annotation:
    return crowsetta.Annotation(
        annot_path=tmp_path / "annotation.txt",
        notated_path=recording.path,
        seq=crowsetta.Sequence.from_segments(
            [
                create_crowsetta_segment(
                    label="dog",
                    onset_s=0.5,
                    offset_s=1.5,
                ),
                create_crowsetta_segment(
                    label="cat",
                    onset_s=2.0,
                    offset_s=2.5,
                ),
            ]
        ),
    )


@pytest.fixture
def bbox_annotation(
    tmp_path: Path,
    recording: data.Recording,
) -> crowsetta.Annotation:
    return crowsetta.Annotation(
        annot_path=tmp_path / "annotation.txt",
        notated_path=recording.path,
        bboxes=[
            crowsetta.BBox(
                onset=0.5,
                low_freq=0.5,
                high_freq=1.5,
                offset=1.5,
                label="dog",
            ),
            crowsetta.BBox(
                onset=2.0,
                low_freq=0.5,
                high_freq=1.5,
                offset=2.5,
                label="cat",
            ),
        ],
    )


def test_seq_annotation_from_clip_annotation(
    clip_annotation: data.ClipAnnotation,
    tmp_path: Path,
):
    annotation = crowsetta_io.annotation_from_clip_annotation(
        clip_annotation,
        annot_path=tmp_path / "annotation.txt",
        annotation_fmt="seq",
    )
    assert isinstance(annotation, crowsetta.Annotation)
    assert isinstance(annotation.seq, crowsetta.Sequence)
    assert len(annotation.seq.segments) == 3


def test_bbox_annotation_from_clip_annotation(
    clip_annotation: data.ClipAnnotation,
    tmp_path: Path,
):
    annotation = crowsetta_io.annotation_from_clip_annotation(
        clip_annotation,
        annot_path=tmp_path / "annotation.txt",
        annotation_fmt="bbox",
    )
    assert isinstance(annotation, crowsetta.Annotation)
    assert isinstance(annotation.bboxes, list)
    assert all(isinstance(bbox, crowsetta.BBox) for bbox in annotation.bboxes)
    # NOTE: there should only be 2 bboxes, not 3, because the TimeInterval
    # are not converted to BBox by default, and errors are ignored.
    assert len(annotation.bboxes) == 2


def test_annotation_from_clip_annotation_fails_with_unknown_fmt(
    clip_annotation: data.ClipAnnotation,
    tmp_path: Path,
):
    with pytest.raises(ValueError):
        crowsetta_io.annotation_from_clip_annotation(
            clip_annotation,
            annot_path=tmp_path / "annotation.txt",
            annotation_fmt="unknown",  # type: ignore
        )


def test_annotation_to_clip_annotation_from_seq(
    sequence_annotation: crowsetta.Annotation,
):
    annotation = crowsetta_io.annotation_to_clip_annotation(
        sequence_annotation,
    )
    assert isinstance(annotation, data.ClipAnnotation)
    assert isinstance(annotation.clip, data.Clip)
    assert len(annotation.sound_events) == 2


def test_annotation_to_clip_annotation_from_bbox(
    bbox_annotation: crowsetta.Annotation,
):
    annotation = crowsetta_io.annotation_to_clip_annotation(
        bbox_annotation,
    )
    assert isinstance(annotation, data.ClipAnnotation)
    assert isinstance(annotation.clip, data.Clip)
    assert len(annotation.sound_events) == 2


def test_annotation_to_clip_annotation_with_notes_and_tags(
    sequence_annotation: crowsetta.Annotation,
    user: data.User,
):
    tags = [
        data.Tag(key="soundscape", value="garden"),
    ]
    annotation = crowsetta_io.annotation_to_clip_annotation(
        sequence_annotation,
        tags=tags,
        notes=[data.Note(message="random note")],
        created_by=user,
    )
    assert isinstance(annotation, data.ClipAnnotation)
    assert isinstance(annotation.clip, data.Clip)
    assert len(annotation.sound_events) == 2


def test_annotation_to_clip_annotation_with_recording(
    sequence_annotation: crowsetta.Annotation,
    recording: data.Recording,
):
    recording = recording.model_copy(
        update=dict(
            latitude=10,
            longitude=10,
            date=datetime.date(2020, 1, 1),
            time=datetime.time(12, 0, 0),
        )
    )
    annotation = crowsetta_io.annotation_to_clip_annotation(
        sequence_annotation,
        recording=recording,
    )
    assert isinstance(annotation, data.ClipAnnotation)
    assert isinstance(annotation.clip, data.Clip)
    assert len(annotation.sound_events) == 2
    assert annotation.clip.recording == recording


def test_annotation_to_clip_annotation_with_recording_kwargs(
    sequence_annotation: crowsetta.Annotation,
):
    annotation = crowsetta_io.annotation_to_clip_annotation(
        sequence_annotation,
        recording_kwargs=dict(
            latitude=10,
            longitude=10,
            date=datetime.date(2020, 1, 1),
            time=datetime.time(12, 0, 0),
        ),
    )
    assert isinstance(annotation, data.ClipAnnotation)
    assert isinstance(annotation.clip, data.Clip)
    assert len(annotation.sound_events) == 2
    assert annotation.clip.recording.latitude == 10
    assert annotation.clip.recording.longitude == 10
    assert annotation.clip.recording.date == datetime.date(2020, 1, 1)
    assert annotation.clip.recording.time == datetime.time(12, 0, 0)


def test_annotation_to_clip_annotation_fails_without_path(tmp_path: Path):
    annotation = crowsetta.Annotation(
        annot_path=tmp_path / "annotation.txt",
        seq=crowsetta.Sequence.from_segments(
            [
                create_crowsetta_segment(
                    label="dog",
                    onset_s=0.5,
                    offset_s=1.5,
                ),
                create_crowsetta_segment(
                    label="cat",
                    onset_s=2.0,
                    offset_s=2.5,
                ),
            ]
        ),
    )

    with pytest.raises(ValueError):
        crowsetta_io.annotation_to_clip_annotation(annotation)


def test_annotation_to_clp_annotation_fails_if_paths_dont_match(
    recording: data.Recording,
    tmp_path: Path,
):
    annotation = crowsetta.Annotation(
        annot_path=tmp_path / "annotation.txt",
        notated_path=tmp_path / "non_existent.wav",
        seq=crowsetta.Sequence.from_segments(
            [
                create_crowsetta_segment(
                    label="dog",
                    onset_s=0.5,
                    offset_s=1.5,
                ),
                create_crowsetta_segment(
                    label="cat",
                    onset_s=2.0,
                    offset_s=2.5,
                ),
            ]
        ),
    )
    assert recording.path != annotation.notated_path

    with pytest.raises(ValueError):
        crowsetta_io.annotation_to_clip_annotation(
            annotation,
            recording=recording,
        )


def test_bbox_annotation_from_clip_annotation_with_incompatible_geoms(
    clip_annotation: data.ClipAnnotation,
    tmp_path: Path,
):
    bbox_annotation = crowsetta_io.annotation_from_clip_annotation(
        clip_annotation,
        annot_path=tmp_path / "annotation.txt",
        annotation_fmt="bbox",
        cast_geometry=False,
    )
    assert isinstance(bbox_annotation, crowsetta.Annotation)
    assert isinstance(bbox_annotation.bboxes, list)
    assert len(bbox_annotation.bboxes) == 1


def test_bbox_annotation_from_clip_annotation_fails_on_incompatible_geoms(
    clip_annotation: data.ClipAnnotation,
    tmp_path: Path,
):
    with pytest.raises(ValueError):
        crowsetta_io.annotation_from_clip_annotation(
            clip_annotation,
            annot_path=tmp_path / "annotation.txt",
            annotation_fmt="bbox",
            cast_geometry=False,
            ignore_errors=False,
        )
