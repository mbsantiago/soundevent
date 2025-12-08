import os
import warnings

os.environ["DISABLE_PANDERA_IMPORT_WARNING"] = "True"

import crowsetta
from crowsetta.examples._examples import EXAMPLES

import soundevent.io.crowsetta as crowsetta_io
from soundevent import data

warnings.filterwarnings("ignore", category=UserWarning, module="crowsetta")


BLACKLIST = [
    "timit",
]


def test_can_import_all_example_formats(recording: data.Recording):
    for example in EXAMPLES:
        if example.format in BLACKLIST:
            continue

        annotation = example.load().to_annot()

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
