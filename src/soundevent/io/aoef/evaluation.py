import datetime
from typing import Dict, List, Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from soundevent import data

from .clip import ClipAdapter, ClipObject
from .clip_annotations import ClipAnnotationsAdapter, ClipAnnotationsObject
from .clip_evaluation import ClipEvaluationAdapter, ClipEvaluationObject
from .clip_predictions import ClipPredictionsAdapter, ClipPredictionsObject
from .match import MatchAdapter, MatchObject
from .note import NoteAdapter
from .recording import RecordingAdapter, RecordingObject
from .sound_event import SoundEventAdapter, SoundEventObject
from .sound_event_annotation import (
    SoundEventAnnotationAdapter,
    SoundEventAnnotationObject,
)
from .sound_event_prediction import (
    SoundEventPredictionAdapter,
    SoundEventPredictionObject,
)
from .tag import TagAdapter, TagObject
from .user import UserAdapter, UserObject


class EvaluationObject(BaseModel):
    collection_type: Literal["evaluation"] = "evaluation"
    uuid: UUID
    created_on: Optional[datetime.datetime] = None
    evaluation_task: str
    users: Optional[List[UserObject]] = None
    tags: Optional[List[TagObject]] = None
    recordings: Optional[List[RecordingObject]] = None
    clips: Optional[List[ClipObject]] = None
    sound_events: Optional[List[SoundEventObject]] = None
    sound_event_annotations: Optional[List[SoundEventAnnotationObject]] = None
    clip_annotations: Optional[List[ClipAnnotationsObject]] = None
    sound_event_predictions: Optional[List[SoundEventPredictionObject]] = None
    clip_predictions: Optional[List[ClipPredictionsObject]] = None
    clip_evaluations: Optional[List[ClipEvaluationObject]] = None
    metrics: Optional[Dict[str, float]] = None
    score: Optional[float] = None
    annotation_set_uuid: Optional[UUID] = None
    annotation_set_created_on: Optional[datetime.datetime] = None
    prediction_set_uuid: Optional[UUID] = None
    prediction_set_created_on: Optional[datetime.datetime] = None
    matches: Optional[List[MatchObject]] = None


class EvaluationAdapter:
    def __init__(
        self,
        audio_dir: Optional[data.PathLike] = None,
        user_adapter: Optional[UserAdapter] = None,
        tag_adapter: Optional[TagAdapter] = None,
        note_adapter: Optional[NoteAdapter] = None,
        recording_adapter: Optional[RecordingAdapter] = None,
        clip_adapter: Optional[ClipAdapter] = None,
        sound_event_adapter: Optional[SoundEventAdapter] = None,
        sound_event_annotation_adapter: Optional[
            SoundEventAnnotationAdapter
        ] = None,
        clip_annotations_adapter: Optional[ClipAnnotationsAdapter] = None,
        sound_event_prediction_adapter: Optional[
            SoundEventPredictionAdapter
        ] = None,
        clip_predictions_adapter: Optional[ClipPredictionsAdapter] = None,
        clip_evaluation_adapter: Optional[ClipEvaluationAdapter] = None,
        match_adapter: Optional[MatchAdapter] = None,
    ):
        self.audio_dir = audio_dir
        self.user_adapter = user_adapter or UserAdapter()
        self.tag_adapter = tag_adapter or TagAdapter()
        self.note_adapter = note_adapter or NoteAdapter(self.user_adapter)
        self.recording_adapter = recording_adapter or RecordingAdapter(
            self.user_adapter,
            self.tag_adapter,
            self.note_adapter,
            audio_dir=self.audio_dir,
        )
        self.clip_adapter = clip_adapter or ClipAdapter(self.recording_adapter)
        self.sound_event_adapter = sound_event_adapter or SoundEventAdapter()
        self.sound_event_annotation_adapter = (
            sound_event_annotation_adapter
            or SoundEventAnnotationAdapter(
                self.user_adapter,
                self.tag_adapter,
                self.note_adapter,
                self.sound_event_adapter,
            )
        )
        self.clip_annotations_adapter = (
            clip_annotations_adapter
            or ClipAnnotationsAdapter(
                self.clip_adapter,
                self.tag_adapter,
                self.note_adapter,
                self.sound_event_annotation_adapter,
            )
        )
        self.sound_event_prediction_adapter = (
            sound_event_prediction_adapter
            or SoundEventPredictionAdapter(
                self.sound_event_adapter,
                self.tag_adapter,
            )
        )
        self.clip_predictions_adapter = (
            clip_predictions_adapter
            or ClipPredictionsAdapter(
                self.clip_adapter,
                self.sound_event_prediction_adapter,
                self.tag_adapter,
            )
        )
        self.match_adapter = match_adapter or MatchAdapter(
            self.sound_event_annotation_adapter,
            self.sound_event_prediction_adapter,
        )
        self.clip_evaluation_adapter = (
            clip_evaluation_adapter
            or ClipEvaluationAdapter(
                self.clip_annotations_adapter,
                self.clip_predictions_adapter,
                self.note_adapter,
                self.match_adapter,
            )
        )

    def to_aoef(self, obj: data.Evaluation) -> EvaluationObject:
        for clip_annotations in obj.annotation_set.clip_annotations:
            self.clip_annotations_adapter.to_aoef(clip_annotations)

        for clip_predictions in obj.prediction_set.clip_predictions:
            self.clip_predictions_adapter.to_aoef(clip_predictions)

        for evaluated_clip in obj.evaluated_clips:
            self.clip_evaluation_adapter.to_aoef(evaluated_clip)

        return EvaluationObject(
            uuid=obj.uuid,
            created_on=obj.created_on,
            evaluation_task=obj.evaluation_task,
            users=self.user_adapter.values(),
            tags=self.tag_adapter.values(),
            recordings=self.recording_adapter.values(),
            clips=self.clip_adapter.values(),
            sound_events=self.sound_event_adapter.values(),
            sound_event_annotations=self.sound_event_annotation_adapter.values(),
            clip_annotations=self.clip_annotations_adapter.values(),
            sound_event_predictions=self.sound_event_prediction_adapter.values(),
            clip_predictions=self.clip_predictions_adapter.values(),
            clip_evaluations=self.clip_evaluation_adapter.values(),
            metrics={
                metric.name: metric.value
                for metric in obj.metrics
                if metric.value is not None
            }
            if obj.metrics
            else None,
            score=obj.score,
            annotation_set_uuid=obj.annotation_set.uuid,
            annotation_set_created_on=obj.annotation_set.created_on,
            prediction_set_uuid=obj.prediction_set.uuid,
            prediction_set_created_on=obj.prediction_set.created_on,
            matches=self.match_adapter.values(),
        )

    def to_soundevent(
        self,
        obj: EvaluationObject,
    ) -> data.Evaluation:
        for user in obj.users or []:
            self.user_adapter.to_soundevent(user)

        for tag in obj.tags or []:
            self.tag_adapter.to_soundevent(tag)

        for recording in obj.recordings or []:
            self.recording_adapter.to_soundevent(recording)

        for clip in obj.clips or []:
            self.clip_adapter.to_soundevent(clip)

        for sound_event in obj.sound_events or []:
            self.sound_event_adapter.to_soundevent(sound_event)

        for sound_event_annotation in obj.sound_event_annotations or []:
            self.sound_event_annotation_adapter.to_soundevent(
                sound_event_annotation
            )

        for clip_annotations in obj.clip_annotations or []:
            self.clip_annotations_adapter.to_soundevent(clip_annotations)

        for sound_event_prediction in obj.sound_event_predictions or []:
            self.sound_event_prediction_adapter.to_soundevent(
                sound_event_prediction
            )

        clip_annotations = [
            self.clip_annotations_adapter.to_soundevent(clip_predictions)
            for clip_predictions in obj.clip_annotations or []
        ]

        clip_predictions = [
            self.clip_predictions_adapter.to_soundevent(evaluated_clip)
            for evaluated_clip in obj.clip_predictions or []
        ]

        for match in obj.matches or []:
            self.match_adapter.to_soundevent(match)

        evaluated_clips = [
            self.clip_evaluation_adapter.to_soundevent(clip_evaluation)
            for clip_evaluation in obj.clip_evaluations or []
        ]

        created_on = obj.created_on or datetime.datetime.now()
        return data.Evaluation(
            uuid=obj.uuid,
            created_on=created_on,
            evaluation_task=obj.evaluation_task,
            annotation_set=data.AnnotationSet(
                uuid=obj.annotation_set_uuid or uuid4(),
                clip_annotations=clip_annotations,
                created_on=obj.annotation_set_created_on or created_on,
            ),
            prediction_set=data.PredictionSet(
                uuid=obj.prediction_set_uuid or uuid4(),
                clip_predictions=clip_predictions,
                created_on=obj.prediction_set_created_on or created_on,
            ),
            evaluated_clips=evaluated_clips,
            score=obj.score,
            metrics=[
                data.Feature(name=name, value=value)
                for name, value in (obj.metrics or {}).items()
            ],
        )
