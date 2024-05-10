"""Module for converting between ClipAnnotation and Crowsetta annotation formats.

This module provides functions to facilitate the interoperability between sound
event data represented in the SoundEvent library's `ClipAnnotation` format and
the `crowsetta.Annotation` format used by the Crowsetta tool.
"""

import os
from pathlib import Path
from typing import List, Literal, Optional, Union

import crowsetta

from soundevent import data
from soundevent.io.crowsetta.bbox import (
    bbox_from_annotation,
    bbox_to_annotation,
)
from soundevent.io.crowsetta.sequence import (
    sequence_from_annotations,
    sequence_to_annotations,
)

PathLike = Union[str, Path, os.PathLike]


__all__ = [
    "annotation_from_clip_annotation",
    "annotation_to_clip_annotation",
]


def annotation_from_clip_annotation(
    annot: data.ClipAnnotation,
    annot_path: PathLike,
    annotation_fmt: Union[Literal["bbox"], Literal["seq"]],
    ignore_errors: bool = True,
    cast_geometry: bool = True,
    **kwargs,
) -> crowsetta.Annotation:
    """Convert a ClipAnnotation to a Crowsetta annotation.

    This function transforms a `ClipAnnotation` object into a Crowsetta
    annotation (`crowsetta.Annotation`). The choice of annotation format
    (`bbox` for bounding boxes or `seq` for sequences) determines the type of
    Crowsetta annotation created. Each sound event within the `ClipAnnotation`
    is individually converted into either a sequence or a bounding boxes using
    the corresponding conversion functions.

    Parameters
    ----------
    annot : data.ClipAnnotation
        The ClipAnnotation object to convert.
    annot_path : PathLike
        The path to the annotation file.
    annotation_fmt : Union[Literal["bbox"], Literal["seq"]]
        The desired Crowsetta annotation format: 'bbox' for bounding boxes or
        'seq' for sequences.
    ignore_errors : bool, optional
        If True, ignore errors during conversion and continue with the next
        sound event, otherwise this function will raise an error if a sound
        event cannot be converted, by default True.
    cast_geometry : bool, optional
        If True, cast non-matching geometries to the expected type, otherwise
        raise an error if the geometry does not match the expected type, by
        default True.
    **kwargs
        Additional keyword arguments passed to the corresponding conversion
        functions.

    Returns
    -------
    crowsetta.Annotation
        A Crowsetta annotation representing the converted ClipAnnotation.
    """
    if annotation_fmt == "bbox":
        bboxes = []
        for annotation in annot.sound_events:
            try:
                bbox = bbox_from_annotation(
                    annotation,
                    cast_to_bbox=cast_geometry,
                    **kwargs,
                )
            except ValueError as e:
                if ignore_errors:
                    continue
                raise e
            bboxes.append(bbox)
        return crowsetta.Annotation(
            annot_path=annot_path,
            notated_path=annot.clip.recording.path,
            bboxes=bboxes,
        )

    if annotation_fmt != "seq":
        raise ValueError(
            "annotation_fmt must be either 'bbox' or 'seq', "
            f"not {annotation_fmt}."
        )

    return crowsetta.Annotation(
        annot_path=annot_path,
        notated_path=annot.clip.recording.path,
        seq=sequence_from_annotations(
            annot.sound_events,
            cast_to_segment=cast_geometry,
            ignore_errors=ignore_errors,
            **kwargs,
        ),
    )


def annotation_to_clip_annotation(
    annot: crowsetta.Annotation,
    recording: Optional[data.Recording] = None,
    tags: Optional[List[data.Tag]] = None,
    notes: Optional[List[data.Note]] = None,
    adjust_time_expansion: bool = True,
    created_by: Optional[data.User] = None,
    recording_kwargs: Optional[dict] = None,
    **kwargs,
) -> data.ClipAnnotation:
    """Convert a Crowsetta annotation to a ClipAnnotation.

    This function transforms a Crowsetta annotation (`crowsetta.Annotation`)
    into a `ClipAnnotation` object. Depending on the annotation format, the
    Crowsetta annotation is converted into a list of sound event annotations or
    sequence annotations, or both, and included in the resulting
    ClipAnnotation.

    Parameters
    ----------
    annot : crowsetta.Annotation
        The Crowsetta annotation to convert.
    recording : Optional[data.Recording], optional
        The original recording associated with the annotations, if not
        provided, it is loaded based on the path of the notated recording, by
        default None.
    tags : Optional[List[data.Tag]], optional
        Tags associated with the clip annotation, by default None.
    notes : Optional[List[data.Note]], optional
        Notes associated with the clip annotation, by default None.
    adjust_time_expansion : bool, optional
        If True, adjust the onset and offset times based on the recording's
        time expansion factor, by default True.
    created_by : Optional[data.User], optional
        User information representing the creator of the converted clip
        annotation, by default None.
    recording_kwargs : Optional[dict], optional
        Additional keyword arguments passed when loading the recording,
        by default None. You can use this to set the recording
        metadata such as `time_expansion`, `latitude`, `longitude`, etc.
    **kwargs
        Additional keyword arguments passed to the conversion functions.

    Returns
    -------
    data.ClipAnnotation
        A ClipAnnotation representing the converted Crowsetta annotation.
    """
    if tags is None:
        tags = []

    if notes is None:
        notes = []

    path = annot.notated_path

    if recording is None:
        if path is None:
            raise ValueError(
                "A recording must be provided if the annotation does not "
                "have an notated path."
            )

        if recording_kwargs is None:
            recording_kwargs = {}

        path = Path(path)  # type: ignore
        recording = data.Recording.from_file(path, **recording_kwargs)

    if path is not None and path != recording.path:
        raise ValueError(
            "The path of the annotation does not match the path of the "
            "recording."
        )

    sound_event_annotations = []
    sequence_annotations = []

    crowsetta_bboxes: List[crowsetta.BBox] = getattr(annot, "bboxes", [])
    for box in crowsetta_bboxes:
        sound_event_annotations.append(
            bbox_to_annotation(
                box,
                recording=recording,
                adjust_time_expansion=adjust_time_expansion,
                created_by=created_by,
                **kwargs,
            )
        )

    crowsetta_sequences: Union[
        List[crowsetta.Sequence], crowsetta.Sequence
    ] = getattr(annot, "seq", [])

    if not isinstance(crowsetta_sequences, list):
        crowsetta_sequences = [crowsetta_sequences]

    for sequence in crowsetta_sequences:
        time_interval_annotations = sequence_to_annotations(
            sequence,
            recording=recording,
            adjust_time_expansion=adjust_time_expansion,
            created_by=created_by,
            **kwargs,
        )
        sound_event_annotations.extend(time_interval_annotations)

        sequence_annotations.append(
            data.SequenceAnnotation(
                sequence=data.Sequence(
                    sound_events=[
                        annotation.sound_event
                        for annotation in time_interval_annotations
                    ]
                ),
                created_by=created_by,
            )
        )

    return data.ClipAnnotation(
        clip=data.Clip(
            recording=recording,
            start_time=0,
            end_time=recording.duration,
        ),
        tags=tags,
        notes=notes,
        sound_events=sound_event_annotations,
        sequences=sequence_annotations,
    )
