import sys
import warnings
from pathlib import Path  # noqa: E402

import crowsetta
import pytest

import soundevent.io.crowsetta as crowsetta_io
from soundevent import data

warnings.filterwarnings("ignore", category=UserWarning, module="crowsetta")


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="requires python3.9 or higher",
)
def test_can_import_all_example_formats(
    tmp_path: Path,
    recording: data.Recording,
):
    data_dir = tmp_path / "crowsetta"
    crowsetta.data.extract_data_files(user_data_dir=data_dir)

    formats = crowsetta.formats.as_list()

    for fmt in formats:
        try:
            example = crowsetta.data.get(fmt, user_data_dir=data_dir)
        except ValueError:
            continue

        scribe = crowsetta.Transcriber(fmt)

        from_file_kwargs = {}
        to_annot_kwargs = {}

        if fmt == "raven":
            from_file_kwargs = {"annot_col": "Species"}

        elif fmt == "simple-seq":
            from_file_kwargs = dict(
                columns_map={
                    "start_seconds": "onset_s",
                    "stop_seconds": "offset_s",
                    "name": "label",
                },
                read_csv_kwargs={"index_col": 0},
            )
        elif fmt == "timit":
            from_file_kwargs = {"audio_path": recording.path}
            to_annot_kwargs = {"samplerate": recording.samplerate}

        annotation = scribe.from_file(
            example.annot_path, **from_file_kwargs
        ).to_annot(**to_annot_kwargs)

        if isinstance(annotation, list):
            annotation = annotation[0]

        assert isinstance(annotation, crowsetta.Annotation)

        if annotation.notated_path is not None:
            recording = recording.model_copy(
                update=dict(path=annotation.notated_path)
            )

        clip_annotation = crowsetta_io.annotation_to_clip_annotation(
            annotation,
            recording=recording,
        )
        assert isinstance(clip_annotation, data.ClipAnnotation)
