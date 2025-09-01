from pathlib import Path

from soundevent import data
from soundevent.transforms import PathTransform


def test_path_transform_changes_recording_path():
    # Given
    recording = data.Recording(
        path=Path("/data/old/recording.wav"),
        duration=10.0,
        channels=1,
        samplerate=44100,
    )
    transformer = PathTransform(lambda path: Path("/data/new/recording.wav"))

    # When
    transformed_recording = transformer.transform_recording(recording)

    # Then
    assert transformed_recording.path == Path("/data/new/recording.wav")


def test_path_transform_is_applied_to_dataset():
    # Given
    recordings = [
        data.Recording(
            path=Path(f"data/old/rec_{i}.wav"),
            duration=1.0,
            channels=1,
            samplerate=16000,
        )
        for i in range(3)
    ]
    dataset = data.Dataset(name="test", recordings=recordings)

    def make_path_relative_to_new_root(path: Path) -> Path:
        return Path("/new_root") / path.name

    transformer = PathTransform(transform=make_path_relative_to_new_root)

    # When
    transformed_dataset = transformer.transform_dataset(dataset)

    # Then
    assert len(transformed_dataset.recordings) == 3
    for i, recording in enumerate(transformed_dataset.recordings):
        assert recording.path == Path(f"/new_root/rec_{i}.wav")


def test_path_transform_is_applied_to_clip_annotation():
    # Given
    recording = data.Recording(
        path=Path("old/path.wav"),
        duration=10.0,
        channels=1,
        samplerate=44100,
    )
    clip = data.Clip(recording=recording, start_time=0, end_time=1)
    annotation = data.ClipAnnotation(clip=clip)

    transformer = PathTransform(lambda path: Path("new/path.wav"))

    # When
    transformed_annotation = transformer.transform_clip_annotation(annotation)

    # Then
    assert transformed_annotation.clip.recording.path == Path("new/path.wav")
