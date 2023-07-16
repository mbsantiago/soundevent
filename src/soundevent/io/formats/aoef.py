"""Acoustic Objects Exchange Format (AOEF) - Data Storage Schema.

The `soundevent.io.format` module provides the schema definition for the
Acoustic Objects Exchange Format (AOEF), a JSON-based format designed to
facilitate the storage and exchange of acoustic data objects. Inspired by the
Common Objects in Context (COCO) format, AOEF offers a standardized and easily
shareable format for researchers working with bioacoustic data.

By utilizing AOEF, researchers can ensure consistency and interoperability when
storing and exchanging acoustic objects. The format leverages Pydantic data
objects for validation, ensuring data integrity and adherence to the defined
schema.

## Benefits of AOEF

* Standardization: AOEF defines a consistent structure for representing acoustic
data objects, enabling seamless sharing and collaboration among researchers.

* Ease of Exchange: The JSON-based format makes it simple to share and exchange
data objects across different platforms and systems.

* Validation and Data Integrity: The schema validation provided by Pydantic
ensures that the data objects conform to the specified structure, reducing the
risk of errors and inconsistencies.

"""
import datetime
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from soundevent import data

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self

__all__ = [
    "TagObject",
    "RecordingObject",
    "DatasetInfoObject",
    "DatasetObject",
    "is_json",
]


class TagObject(BaseModel):
    """Schema definition for a tag object in AOEF format."""

    id: int

    key: str

    value: str

    @classmethod
    def from_tag(
        cls,
        tag: data.Tag,
        tags: Dict[data.Tag, Self],
    ) -> Self:
        """Convert a tag to a tag object."""
        if tag in tags:
            return tags[tag]

        tags[tag] = cls(
            id=len(tags),
            key=tag.key,
            value=tag.value,
        )

        return tags[tag]

    def to_tag(self) -> data.Tag:
        """Convert a tag object to a tag."""
        return data.Tag(
            key=self.key,
            value=self.value,
        )


class RecordingObject(BaseModel):
    """Schema definition for a recording object in AOEF format."""

    id: int

    uuid: Optional[UUID] = None

    path: Path

    duration: float

    channels: int

    samplerate: int

    time_expansion: Optional[float] = None

    hash: Optional[str] = None

    date: Optional[datetime.date] = None

    time: Optional[datetime.time] = None

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    tags: Optional[List[int]] = None

    features: Optional[Dict[str, float]] = None

    notes: Optional[List[data.Note]] = None

    @classmethod
    def from_recording(
        cls,
        recording: data.Recording,
        recordings: Dict[data.Recording, Self],
        tags: Dict[data.Tag, TagObject],
        audio_dir: Optional[Path] = None,
    ) -> Self:
        """Convert a recording to a recording object."""
        if recording in recordings:
            return recordings[recording]

        path = recording.path
        if audio_dir is not None:
            path = path.resolve().relative_to(audio_dir)

        tag_ids = [TagObject.from_tag(tag, tags).id for tag in recording.tags]

        features = {
            feature.name: feature.value for feature in recording.features
        }

        recordings[recording] = cls(
            id=len(recordings),
            uuid=recording.id,
            path=path,
            duration=recording.duration,
            channels=recording.channels,
            samplerate=recording.samplerate,
            time_expansion=recording.time_expansion
            if recording.time_expansion != 1.0
            else None,
            hash=recording.hash,
            date=recording.date,
            time=recording.time,
            latitude=recording.latitude,
            longitude=recording.longitude,
            tags=tag_ids if tag_ids else None,
            features=features if features else None,
            notes=recording.notes if recording.notes else None,
        )

        return recordings[recording]

    def to_recording(
        self,
        tags: Dict[int, data.Tag],
        audio_dir: Optional[Path] = None,
    ) -> data.Recording:
        """Convert a recording object to a recording."""
        path = self.path

        if audio_dir is not None:
            path = audio_dir / path

        return data.Recording(
            id=self.uuid or uuid4(),
            path=path,
            duration=self.duration,
            channels=self.channels,
            samplerate=self.samplerate,
            time_expansion=self.time_expansion if self.time_expansion else 1.0,
            hash=self.hash,
            date=self.date,
            time=self.time,
            latitude=self.latitude,
            longitude=self.longitude,
            tags=[tags[tag_id] for tag_id in (self.tags or [])],
            features=[
                data.Feature(
                    name=name,
                    value=value,
                )
                for name, value in (self.features or {}).items()
            ],
            notes=self.notes if self.notes else [],
        )


class DatasetInfoObject(BaseModel):
    """Schema definition for a dataset info object in AOEF format."""

    uuid: Optional[UUID] = None
    """The unique identifier of the dataset."""

    name: str
    """The name of the dataset."""

    description: Optional[str] = None
    """A description of the dataset."""

    date_created: datetime.datetime
    """The date and time at which the file dataset was created."""

    @classmethod
    def from_dataset(
        cls,
        dataset: data.Dataset,
        date_created: Optional[datetime.datetime] = None,
    ) -> Self:
        """Convert a dataset to a dataset info object."""
        if date_created is None:
            date_created = datetime.datetime.now()

        return cls(
            uuid=dataset.id,
            name=dataset.name,
            description=dataset.description,
            date_created=date_created,
        )


class DatasetObject(BaseModel):
    """Schema definition for a dataset object in AOEF format."""

    info: DatasetInfoObject

    tags: Optional[List[TagObject]] = None

    recordings: List[RecordingObject]

    @classmethod
    def from_dataset(
        cls,
        dataset: data.Dataset,
        audio_dir: Optional[Path] = None,
        date_created: Optional[datetime.datetime] = None,
    ) -> Self:
        """Convert a dataset to a dataset object."""
        tags: Dict[data.Tag, TagObject] = {}
        recordings: Dict[data.Recording, RecordingObject] = {}

        recording_list = [
            RecordingObject.from_recording(
                recording,
                recordings,
                tags,
                audio_dir=audio_dir,
            )
            for recording in dataset.recordings
        ]

        return cls(
            info=DatasetInfoObject.from_dataset(dataset, date_created),
            tags=list(tags.values()) if tags else None,
            recordings=recording_list,
        )

    def to_dataset(
        self,
        audio_dir: Optional[Path] = None,
    ) -> data.Dataset:
        """Convert a dataset object to a dataset."""
        tags = {tag.id: tag.to_tag() for tag in self.tags or []}

        recordings = [
            recording.to_recording(tags=tags, audio_dir=audio_dir)
            for recording in self.recordings
        ]

        return data.Dataset(
            id=self.info.uuid or uuid4(),
            name=self.info.name,
            description=self.info.description,
            recordings=recordings,
        )


class ClipObject(BaseModel):
    """Schema definition for a clip object in AOEF format."""

    id: int

    recording: int

    uuid: Optional[UUID] = None

    start_time: float

    end_time: float

    tags: Optional[List[int]] = None

    features: Optional[Dict[str, float]] = None

    notes: Optional[List[data.Note]] = None

    @classmethod
    def from_clip(
        cls,
        clip: data.Clip,
        clips: Dict[data.Clip, Self],
        recordings: Dict[data.Recording, RecordingObject],
        tags: Dict[data.Tag, TagObject],
        audio_dir: Optional[Path] = None,
    ) -> Self:
        """Convert a clip to a clip object."""
        if clip in clips:
            return clips[clip]

        tag_ids = [TagObject.from_tag(tag, tags).id for tag in clip.tags]

        features = {feature.name: feature.value for feature in clip.features}

        clips[clip] = cls(
            id=len(clips),
            recording=RecordingObject.from_recording(
                clip.recording,
                recordings,
                tags,
                audio_dir=audio_dir,
            ).id,
            uuid=clip.uuid,
            start_time=clip.start_time,
            end_time=clip.end_time,
            tags=tag_ids if tag_ids else None,
            features=features if features else None,
        )

        return clips[clip]

    def to_clip(
        self,
        tags: Dict[int, data.Tag],
        recordings: Dict[int, data.Recording],
    ) -> data.Clip:
        if self.recording not in recordings:
            raise ValueError(f"Recording with ID {self.recording} not found.")

        return data.Clip(
            uuid=self.uuid or uuid4(),
            recording=recordings[self.recording],
            start_time=self.start_time,
            end_time=self.end_time,
            tags=[tags[tag_id] for tag_id in (self.tags or [])],
            features=[
                data.Feature(
                    name=name,
                    value=value,
                )
                for name, value in (self.features or {}).items()
            ],
        )


class SoundEventObject(BaseModel):
    """Schema definition for a sound event object in AOEF format."""

    id: int

    recording: int

    geometry: Optional[data.Geometry] = None

    uuid: Optional[UUID] = None

    tags: Optional[List[int]] = None

    features: Optional[Dict[str, float]] = None

    @classmethod
    def from_sound_event(
        cls,
        sound_event: data.SoundEvent,
        sound_events: Dict[data.SoundEvent, Self],
        recordings: Dict[data.Recording, RecordingObject],
        tags: Dict[data.Tag, TagObject],
        audio_dir: Optional[Path] = None,
    ) -> Self:
        """Convert a sound event to a sound event object."""
        if sound_event in sound_events:
            return sound_events[sound_event]

        tag_ids = [
            TagObject.from_tag(tag, tags).id for tag in sound_event.tags
        ]

        features = {
            feature.name: feature.value for feature in sound_event.features
        }

        sound_events[sound_event] = cls(
            id=len(sound_events),
            recording=RecordingObject.from_recording(
                sound_event.recording,
                recordings,
                tags,
                audio_dir=audio_dir,
            ).id,
            geometry=sound_event.geometry,
            uuid=sound_event.uuid,
            tags=tag_ids if tag_ids else None,
            features=features if features else None,
        )

        return sound_events[sound_event]

    def to_sound_event(
        self,
        recordings: Dict[int, data.Recording],
        tags: Dict[int, data.Tag],
    ) -> data.SoundEvent:
        if self.recording not in recordings:
            raise ValueError(f"Recording with ID {self.recording} not found.")

        return data.SoundEvent(
            uuid=self.uuid or uuid4(),
            recording=recordings[self.recording],
            geometry=self.geometry,
            tags=[tags[tag_id] for tag_id in (self.tags or [])],
            features=[
                data.Feature(
                    name=name,
                    value=value,
                )
                for name, value in (self.features or {}).items()
            ],
        )


class AnnotationObject(BaseModel):
    """Schema definition for an annotation object in AOEF format."""

    id: int

    sound_event: int

    notes: Optional[List[data.Note]] = None

    tags: Optional[List[int]] = None

    uuid: Optional[UUID] = None

    created_by: Optional[str] = None

    created_on: Optional[datetime.datetime] = None

    @classmethod
    def from_annotation(
        cls,
        annotation: data.Annotation,
        annotations: Dict[data.Annotation, Self],
        sound_events: Dict[data.SoundEvent, SoundEventObject],
        recordings: Dict[data.Recording, RecordingObject],
        tags: Dict[data.Tag, TagObject],
        audio_dir: Optional[Path] = None,
    ) -> Self:
        """Convert an annotation to an annotation object."""
        if annotation in annotations:
            return annotations[annotation]

        tag_ids = [TagObject.from_tag(tag, tags).id for tag in annotation.tags]

        annotations[annotation] = cls(
            id=len(annotations),
            sound_event=SoundEventObject.from_sound_event(
                annotation.sound_event,
                sound_events,
                recordings,
                tags,
                audio_dir=audio_dir,
            ).id,
            notes=annotation.notes if annotation.notes else None,
            tags=tag_ids if tag_ids else None,
            uuid=annotation.id,
            created_by=annotation.created_by,
            created_on=annotation.created_on,
        )

        return annotations[annotation]

    def to_annotation(
        self,
        sound_events: Dict[int, data.SoundEvent],
        tags: Dict[int, data.Tag],
    ) -> data.Annotation:
        if self.sound_event not in sound_events:
            raise ValueError(
                f"Sound event with ID {self.sound_event} not found."
            )

        return data.Annotation(
            id=self.uuid or uuid4(),
            sound_event=sound_events[self.sound_event],
            notes=self.notes if self.notes else [],
            tags=[tags[tag_id] for tag_id in (self.tags or [])],
            created_by=self.created_by,
            created_on=self.created_on,
        )


class AnnotationTaskObject(BaseModel):
    """Schema definition for an annotation task object in AOEF format."""

    id: int

    uuid: Optional[UUID] = None

    clip: int

    annotations: Optional[List[int]] = None

    completed_by: Optional[str] = None

    completed_on: Optional[datetime.datetime] = None

    completed: bool

    notes: Optional[List[data.Note]] = None

    tags: Optional[List[int]] = None

    @classmethod
    def from_annotation_task(
        cls,
        task: data.AnnotationTask,
        tasks: Dict[data.AnnotationTask, Self],
        clips: Dict[data.Clip, ClipObject],
        annotations: Dict[data.Annotation, AnnotationObject],
        sound_events: Dict[data.SoundEvent, SoundEventObject],
        recordings: Dict[data.Recording, RecordingObject],
        tags: Dict[data.Tag, TagObject],
        audio_dir: Optional[Path] = None,
    ) -> Self:
        """Convert an annotation task to an annotation task object."""
        if task in tasks:
            return tasks[task]

        annotation_ids = [
            AnnotationObject.from_annotation(
                annotation,
                annotations,
                sound_events,
                recordings,
                tags,
                audio_dir=audio_dir,
            ).id
            for annotation in task.annotations
        ]

        tag_ids = [TagObject.from_tag(tag, tags).id for tag in task.tags]

        tasks[task] = cls(
            id=len(tasks),
            uuid=task.id,
            clip=ClipObject.from_clip(
                task.clip,
                clips=clips,
                recordings=recordings,
                tags=tags,
                audio_dir=audio_dir,
            ).id,
            annotations=annotation_ids if annotation_ids else None,
            completed_by=task.completed_by,
            completed_on=task.completed_on,
            completed=task.completed,
            notes=task.notes if task.notes else None,
            tags=tag_ids if tag_ids else None,
        )

        return tasks[task]

    def to_annotation_task(
        self,
        clips: Dict[int, data.Clip],
        annotations: Dict[int, data.Annotation],
        tags: Dict[int, data.Tag],
    ) -> data.AnnotationTask:
        if self.clip not in clips:
            raise ValueError(f"Clip with ID {self.clip} not found.")

        return data.AnnotationTask(
            id=self.uuid or uuid4(),
            clip=clips[self.clip],
            annotations=[
                annotations[annotation_id]
                for annotation_id in (self.annotations or [])
            ],
            completed_by=self.completed_by,
            completed_on=self.completed_on,
            completed=self.completed,
            notes=self.notes if self.notes else [],
            tags=[tags[tag_id] for tag_id in (self.tags or [])],
        )


class AnnotationProjectInfo(BaseModel):
    """Schema definition for an annotation project info object in AOEF format."""

    uuid: UUID

    name: str

    description: Optional[str] = None

    date_created: datetime.datetime

    instructions: Optional[str] = None

    @classmethod
    def from_annotation_project(
        cls,
        project: data.AnnotationProject,
        date_created: Optional[datetime.datetime] = None,
    ) -> Self:
        """Convert an annotation project to an annotation project info object."""
        if date_created is None:
            date_created = datetime.datetime.now()

        return cls(
            uuid=project.id,
            name=project.name,
            description=project.description,
            date_created=date_created,
            instructions=project.instructions,
        )


class AnnotationProjectObject(BaseModel):
    """Schema definition for an annotation project object in AOEF format."""

    info: AnnotationProjectInfo

    tags: Optional[List[TagObject]] = None

    recordings: Optional[List[RecordingObject]] = None

    clips: Optional[List[ClipObject]] = None

    sound_events: Optional[List[SoundEventObject]] = None

    annotations: Optional[List[AnnotationObject]] = None

    tasks: Optional[List[AnnotationTaskObject]] = None

    @classmethod
    def from_annotation_project(
        cls,
        project: data.AnnotationProject,
        audio_dir: Optional[Path] = None,
        date_created: Optional[datetime.datetime] = None,
    ) -> Self:
        """Convert an annotation project to an annotation project object."""
        tasks: Dict[data.AnnotationTask, AnnotationTaskObject] = {}
        tags: Dict[data.Tag, TagObject] = {}
        clips: Dict[data.Clip, ClipObject] = {}
        recordings: Dict[data.Recording, RecordingObject] = {}
        sound_events: Dict[data.SoundEvent, SoundEventObject] = {}
        annotations: Dict[data.Annotation, AnnotationObject] = {}

        if date_created is None:
            date_created = datetime.datetime.now()

        annotation_task_list = [
            AnnotationTaskObject.from_annotation_task(
                task,
                tasks,
                clips,
                annotations,
                sound_events,
                recordings,
                tags,
                audio_dir=audio_dir,
            )
            for task in project.tasks
        ]

        info = AnnotationProjectInfo.from_annotation_project(
            project,
            date_created=date_created,
        )

        return cls(
            info=info,
            tags=list(tags.values()) if tags else None,
            clips=list(clips.values()) if clips else None,
            recordings=list(recordings.values()) if recordings else None,
            sound_events=list(sound_events.values()) if sound_events else None,
            annotations=list(annotations.values()) if annotations else None,
            tasks=annotation_task_list if annotation_task_list else None,
        )

    def to_annotation_project(
        self,
        audio_dir: Optional[Path] = None,
    ) -> data.AnnotationProject:
        """Convert an annotation project object to an annotation project."""
        tags: Dict[int, data.Tag] = {}
        clips: Dict[int, data.Clip] = {}
        recordings: Dict[int, data.Recording] = {}
        sound_events: Dict[int, data.SoundEvent] = {}
        annotations: Dict[int, data.Annotation] = {}
        tasks: Dict[int, data.AnnotationTask] = {}

        for tag in self.tags or []:
            tags[tag.id] = tag.to_tag()

        for recording in self.recordings or []:
            recordings[recording.id] = recording.to_recording(
                tags=tags,
                audio_dir=audio_dir,
            )

        for clip in self.clips or []:
            clips[clip.id] = clip.to_clip(
                tags=tags,
                recordings=recordings,
            )

        for sound_event in self.sound_events or []:
            sound_events[sound_event.id] = sound_event.to_sound_event(
                recordings=recordings,
                tags=tags,
            )

        for annotation in self.annotations or []:
            annotations[annotation.id] = annotation.to_annotation(
                sound_events=sound_events,
                tags=tags,
            )

        for task in self.tasks or []:
            tasks[task.id] = task.to_annotation_task(
                clips=clips,
                annotations=annotations,
                tags=tags,
            )

        return data.AnnotationProject(
            id=self.info.uuid,
            name=self.info.name,
            description=self.info.description,
            instructions=self.info.instructions,
            tasks=list(tasks.values()),
        )


class PredictedSoundEventObject(BaseModel):
    id: int

    uuid: UUID

    sound_event: int

    score: float = Field(..., ge=0.0, le=1.0)

    tags: Optional[List[Tuple[int, float]]] = None

    features: Optional[Dict[str, float]] = None

    @classmethod
    def from_predicted_sound_event(
        cls,
        predicted_sound_event: data.PredictedSoundEvent,
        predicted_sound_events: Dict[data.PredictedSoundEvent, Self],
        recordings: Dict[data.Recording, RecordingObject],
        sound_events: Dict[data.SoundEvent, SoundEventObject],
        tags: Dict[data.Tag, TagObject],
        audio_dir: Optional[Path] = None,
    ) -> Self:
        """Convert a predicted sound event to a predicted sound event object."""
        if predicted_sound_event in predicted_sound_events:
            return predicted_sound_events[predicted_sound_event]

        predicted_tags = [
            (TagObject.from_tag(tag.tag, tags).id, tag.score)
            for tag in predicted_sound_event.tags
        ]

        predicted_sound_events[predicted_sound_event] = cls(
            id=len(predicted_sound_events),
            uuid=predicted_sound_event.id,
            sound_event=SoundEventObject.from_sound_event(
                predicted_sound_event.sound_event,
                sound_events=sound_events,
                recordings=recordings,
                tags=tags,
                audio_dir=audio_dir,
            ).id,
            score=predicted_sound_event.score,
            tags=predicted_tags if predicted_tags else None,
            features={
                feature.name: feature.value
                for feature in predicted_sound_event.features
            }
            if predicted_sound_event.features
            else None,
        )

        return predicted_sound_events[predicted_sound_event]

    def to_predicted_sound_event(
        self,
        sound_events: Dict[int, data.SoundEvent],
        tags: Dict[int, data.Tag],
    ) -> data.PredictedSoundEvent:
        """Convert a predicted sound event object to a predicted sound event."""
        if self.sound_event not in sound_events:
            raise ValueError(
                f"Sound event with ID {self.sound_event} not found "
                "in sound events."
            )

        return data.PredictedSoundEvent(
            id=self.uuid,
            sound_event=sound_events[self.sound_event],
            score=self.score,
            tags=[
                data.PredictedTag(
                    tag=tags[tag[0]],
                    score=tag[1],
                )
                for tag in self.tags or []
            ],
            features=[
                data.Feature(
                    name=feature[0],
                    value=feature[1],
                )
                for feature in (self.features or {}).items()
            ],
        )


class ProcessedClipObject(BaseModel):
    id: int

    uuid: UUID

    clip: int

    sound_events: Optional[List[int]] = None

    tags: Optional[List[Tuple[int, float]]] = None

    features: Optional[Dict[str, float]] = None

    @classmethod
    def from_processed_clip(
        cls,
        processed_clip: data.ProcessedClip,
        processed_clips: Dict[data.ProcessedClip, Self],
        recordings: Dict[data.Recording, RecordingObject],
        clips: Dict[data.Clip, ClipObject],
        tags: Dict[data.Tag, TagObject],
        sound_events: Dict[data.SoundEvent, SoundEventObject],
        predicted_sound_events: Dict[
            data.PredictedSoundEvent, PredictedSoundEventObject
        ],
        audio_dir: Optional[Path] = None,
    ) -> Self:
        """Convert a processed clip to a processed clip object."""
        if processed_clip in processed_clips:
            return processed_clips[processed_clip]

        predicted_sound_events_ids = [
            PredictedSoundEventObject.from_predicted_sound_event(
                sound_event,
                predicted_sound_events=predicted_sound_events,
                recordings=recordings,
                sound_events=sound_events,
                tags=tags,
                audio_dir=audio_dir,
            ).id
            for sound_event in processed_clip.sound_events
        ]

        predicted_tags = [
            (TagObject.from_tag(tag.tag, tags).id, tag.score)
            for tag in processed_clip.tags
        ]

        return cls(
            id=len(processed_clips),
            uuid=processed_clip.uuid,
            clip=ClipObject.from_clip(
                processed_clip.clip,
                clips=clips,
                recordings=recordings,
                tags=tags,
                audio_dir=audio_dir,
            ).id,
            sound_events=predicted_sound_events_ids
            if predicted_sound_events_ids
            else None,
            tags=predicted_tags if predicted_tags else None,
            features={
                feature.name: feature.value
                for feature in processed_clip.features
            }
            if processed_clip.features
            else None,
        )

    def to_processed_clip(
        self,
        clips: Dict[int, data.Clip],
        predicted_sound_events: Dict[int, data.PredictedSoundEvent],
        tags: Dict[int, data.Tag],
    ) -> data.ProcessedClip:
        """Convert a processed clip object to a processed clip."""
        if self.clip not in clips:
            raise ValueError(f"Clip with ID {self.clip} not found in clips.")

        return data.ProcessedClip(
            uuid=self.uuid,
            clip=clips[self.clip],
            sound_events=[
                predicted_sound_events[sound_event]
                for sound_event in (self.sound_events or [])
            ],
            tags=[
                data.PredictedTag(
                    tag=tags[tag[0]],
                    score=tag[1],
                )
                for tag in self.tags or []
            ],
            features=[
                data.Feature(
                    name=feature[0],
                    value=feature[1],
                )
                for feature in (self.features or {}).items()
            ],
        )


class ModelRunInfo(BaseModel):
    uuid: UUID

    model: str

    description: Optional[str] = None

    run_date: datetime.datetime

    date_created: datetime.datetime

    @classmethod
    def from_model_run(
        cls,
        model_run: data.ModelRun,
        date_created: Optional[datetime.datetime] = None,
    ) -> Self:
        """Convert a model run to a model run object."""
        if date_created is None:
            date_created = datetime.datetime.now()
        return cls(
            uuid=model_run.id,
            model=model_run.model,
            run_date=model_run.created_on,
            date_created=date_created,
        )


class ModelRunObject(BaseModel):
    info: ModelRunInfo

    tags: Optional[List[TagObject]] = None

    recordings: Optional[List[RecordingObject]] = None

    clips: Optional[List[ClipObject]] = None

    processed_clips: Optional[List[ProcessedClipObject]] = None

    sound_events: Optional[List[SoundEventObject]] = None

    predicted_sound_events: Optional[List[PredictedSoundEventObject]] = None

    @classmethod
    def from_model_run(
        cls,
        model_run: data.ModelRun,
        audio_dir: Optional[Path] = None,
        date_created: Optional[datetime.datetime] = None,
    ) -> Self:
        """Convert a model run to a model run object."""
        if date_created is None:
            date_created = datetime.datetime.now()

        processed_clips: Dict[data.ProcessedClip, ProcessedClipObject] = {}
        recordings: Dict[data.Recording, RecordingObject] = {}
        clips: Dict[data.Clip, ClipObject] = {}
        tags: Dict[data.Tag, TagObject] = {}
        sound_events: Dict[data.SoundEvent, SoundEventObject] = {}
        predicted_sound_events: Dict[
            data.PredictedSoundEvent, PredictedSoundEventObject
        ] = {}

        processed_clips_list = [
            ProcessedClipObject.from_processed_clip(
                processed_clip,
                processed_clips=processed_clips,
                recordings=recordings,
                clips=clips,
                tags=tags,
                sound_events=sound_events,
                predicted_sound_events=predicted_sound_events,
                audio_dir=audio_dir,
            )
            for processed_clip in model_run.clips
        ]

        return cls(
            info=ModelRunInfo.from_model_run(
                model_run,
                date_created=date_created,
            ),
            clips=list(clips.values()) if clips else None,
            tags=list(tags.values()) if tags else None,
            recordings=list(recordings.values()) if recordings else None,
            sound_events=list(sound_events.values()) if sound_events else None,
            predicted_sound_events=list(predicted_sound_events.values())
            if predicted_sound_events
            else None,
            processed_clips=processed_clips_list,
        )

    def to_model_run(
        self,
        audio_dir: Optional[Path] = None,
    ) -> data.ModelRun:
        """Convert a model run object to a model run."""
        tags: Dict[int, data.Tag] = {}
        recordings: Dict[int, data.Recording] = {}
        clips: Dict[int, data.Clip] = {}
        sound_events: Dict[int, data.SoundEvent] = {}
        predicted_sound_events: Dict[int, data.PredictedSoundEvent] = {}
        processed_clips: Dict[int, data.ProcessedClip] = {}

        for tag in self.tags or []:
            tags[tag.id] = tag.to_tag()

        for recording in self.recordings or []:
            recordings[recording.id] = recording.to_recording(
                tags=tags, audio_dir=audio_dir
            )

        for clip in self.clips or []:
            clips[clip.id] = clip.to_clip(
                tags=tags,
                recordings=recordings,
            )

        for sound_event in self.sound_events or []:
            sound_events[sound_event.id] = sound_event.to_sound_event(
                recordings=recordings,
                tags=tags,
            )

        for predicted_sound_event in self.predicted_sound_events or []:
            predicted_sound_events[
                predicted_sound_event.id
            ] = predicted_sound_event.to_predicted_sound_event(
                sound_events=sound_events,
                tags=tags,
            )

        for processed_clip in self.processed_clips or []:
            processed_clips[
                processed_clip.id
            ] = processed_clip.to_processed_clip(
                clips=clips,
                predicted_sound_events=predicted_sound_events,
                tags=tags,
            )

        return data.ModelRun(
            id=self.info.uuid,
            model=self.info.model,
            created_on=self.info.run_date,
            clips=list(processed_clips.values()),
        )


def is_json(path: Union[str, os.PathLike]) -> bool:
    """Check if a file is a JSON file."""
    path = Path(path)
    return path.suffix == ".json"
