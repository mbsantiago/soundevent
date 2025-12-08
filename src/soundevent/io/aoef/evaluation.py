import datetime
from typing import Dict, List, Literal
from uuid import UUID

from pydantic import BaseModel

from .clip import ClipAdapter, ClipObject
from .clip_annotations import ClipAnnotationsAdapter, ClipAnnotationsObject
from .clip_evaluation import ClipEvaluationAdapter, ClipEvaluationObject
from .clip_predictions import ClipPredictionsAdapter, ClipPredictionsObject
from .match import MatchAdapter, MatchObject
from .note import NoteAdapter
from .recording import RecordingAdapter, RecordingObject
from .sequence import SequenceAdapter, SequenceObject
from .sequence_annotation import (
    SequenceAnnotationAdapter,
    SequenceAnnotationObject,
)
from .sequence_prediction import (
    SequencePredictionAdapter,
    SequencePredictionObject,
)
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
from soundevent import data


class EvaluationObject(BaseModel):
    uuid: UUID
    collection_type: Literal["evaluation"] = "evaluation"
    created_on: datetime.datetime | None = None
    evaluation_task: str
    users: List[UserObject] | None = None
    tags: List[TagObject] | None = None
    recordings: List[RecordingObject] | None = None
    clips: List[ClipObject] | None = None
    sound_events: List[SoundEventObject] | None = None
    sequences: List[SequenceObject] | None = None
    sound_event_annotations: List[SoundEventAnnotationObject] | None = None
    sequence_annotations: List[SequenceAnnotationObject] | None = None
    clip_annotations: List[ClipAnnotationsObject] | None = None
    sound_event_predictions: List[SoundEventPredictionObject] | None = None
    sequence_predictions: List[SequencePredictionObject] | None = None
    clip_predictions: List[ClipPredictionsObject] | None = None
    clip_evaluations: List[ClipEvaluationObject] | None = None
    metrics: Dict[str, float] | None = None
    score: float | None = None
    matches: List[MatchObject] | None = None


class EvaluationAdapter:
    def __init__(
        self,
        audio_dir: data.PathLike | None = None,
        user_adapter: UserAdapter | None = None,
        tag_adapter: TagAdapter | None = None,
        note_adapter: NoteAdapter | None = None,
        recording_adapter: RecordingAdapter | None = None,
        sound_event_adapter: SoundEventAdapter | None = None,
        sequence_adapter: SequenceAdapter | None = None,
        clip_adapter: ClipAdapter | None = None,
        sound_event_annotation_adapter: SoundEventAnnotationAdapter
        | None = None,
        sequence_annotation_adapter: SequenceAnnotationAdapter | None = None,
        clip_annotations_adapter: ClipAnnotationsAdapter | None = None,
        sound_event_prediction_adapter: SoundEventPredictionAdapter
        | None = None,
        sequence_prediction_adapter: SequencePredictionAdapter | None = None,
        clip_predictions_adapter: ClipPredictionsAdapter | None = None,
        clip_evaluation_adapter: ClipEvaluationAdapter | None = None,
        match_adapter: MatchAdapter | None = None,
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
        self.sound_event_adapter = sound_event_adapter or SoundEventAdapter(
            self.recording_adapter
        )
        self.sequence_adapter = sequence_adapter or SequenceAdapter(
            self.sound_event_adapter
        )
        self.clip_adapter = clip_adapter or ClipAdapter(self.recording_adapter)
        self.sound_event_annotation_adapter = (
            sound_event_annotation_adapter
            or SoundEventAnnotationAdapter(
                self.user_adapter,
                self.tag_adapter,
                self.note_adapter,
                self.sound_event_adapter,
            )
        )
        self.sequence_annotation_adapter = (
            sequence_annotation_adapter
            or SequenceAnnotationAdapter(
                self.user_adapter,
                self.tag_adapter,
                self.note_adapter,
                self.sequence_adapter,
            )
        )
        self.clip_annotations_adapter = (
            clip_annotations_adapter
            or ClipAnnotationsAdapter(
                self.clip_adapter,
                self.tag_adapter,
                self.note_adapter,
                self.sound_event_annotation_adapter,
                self.sequence_annotation_adapter,
            )
        )
        self.sound_event_prediction_adapter = (
            sound_event_prediction_adapter
            or SoundEventPredictionAdapter(
                self.sound_event_adapter,
                self.tag_adapter,
            )
        )
        self.sequence_prediction_adapter = (
            sequence_prediction_adapter
            or SequencePredictionAdapter(
                self.sequence_adapter,
                self.tag_adapter,
            )
        )
        self.clip_predictions_adapter = (
            clip_predictions_adapter
            or ClipPredictionsAdapter(
                self.clip_adapter,
                self.sound_event_prediction_adapter,
                self.tag_adapter,
                self.sequence_prediction_adapter,
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
        for evaluated_clip in obj.clip_evaluations:
            self.clip_evaluation_adapter.to_aoef(evaluated_clip)

        return EvaluationObject(
            uuid=obj.uuid,
            created_on=obj.created_on,
            evaluation_task=obj.evaluation_task,
            users=self.user_adapter.values(),
            tags=self.tag_adapter.values(),
            recordings=self.recording_adapter.values(),
            sound_events=self.sound_event_adapter.values(),
            sequences=self.sequence_adapter.values(),
            clips=self.clip_adapter.values(),
            sound_event_annotations=self.sound_event_annotation_adapter.values(),
            sequence_annotations=self.sequence_annotation_adapter.values(),
            clip_annotations=self.clip_annotations_adapter.values(),
            sound_event_predictions=self.sound_event_prediction_adapter.values(),
            sequence_predictions=self.sequence_prediction_adapter.values(),
            clip_predictions=self.clip_predictions_adapter.values(),
            clip_evaluations=self.clip_evaluation_adapter.values(),
            metrics=(
                {
                    data.key_from_term(metric.term): metric.value
                    for metric in obj.metrics
                    if metric.value is not None
                }
                if obj.metrics
                else None
            ),
            score=obj.score,
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

        for sound_event in obj.sound_events or []:
            self.sound_event_adapter.to_soundevent(sound_event)

        for sequence in obj.sequences or []:
            self.sequence_adapter.to_soundevent(sequence)

        for clip in obj.clips or []:
            self.clip_adapter.to_soundevent(clip)

        for sound_event_annotation in obj.sound_event_annotations or []:
            self.sound_event_annotation_adapter.to_soundevent(
                sound_event_annotation
            )

        for sequence_annotation in obj.sequence_annotations or []:
            self.sequence_annotation_adapter.to_soundevent(sequence_annotation)

        for clip_annotation in obj.clip_annotations or []:
            self.clip_annotations_adapter.to_soundevent(clip_annotation)

        for sound_event_prediction in obj.sound_event_predictions or []:
            self.sound_event_prediction_adapter.to_soundevent(
                sound_event_prediction
            )

        for sequence_prediction in obj.sequence_predictions or []:
            self.sequence_prediction_adapter.to_soundevent(sequence_prediction)

        for clip_prediction in obj.clip_predictions or []:
            self.clip_predictions_adapter.to_soundevent(clip_prediction)

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
            clip_evaluations=evaluated_clips,
            score=obj.score,
            metrics=[
                data.Feature(term=data.term_from_key(name), value=value)
                for name, value in (obj.metrics or {}).items()
            ],
        )
