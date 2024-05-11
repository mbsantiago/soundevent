import datetime
from typing import List, Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from .clip import ClipAdapter, ClipObject
from .clip_predictions import ClipPredictionsAdapter, ClipPredictionsObject
from .note import NoteAdapter
from .recording import RecordingAdapter, RecordingObject
from .sequence import SequenceAdapter, SequenceObject
from .sequence_prediction import (
    SequencePredictionAdapter,
    SequencePredictionObject,
)
from .sound_event import SoundEventAdapter, SoundEventObject
from .sound_event_prediction import (
    SoundEventPredictionAdapter,
    SoundEventPredictionObject,
)
from .tag import TagAdapter, TagObject
from .user import UserAdapter, UserObject
from soundevent import data


class PredictionSetObject(BaseModel):
    uuid: UUID
    created_on: Optional[datetime.datetime] = None
    collection_type: Literal["prediction_set"] = "prediction_set"
    users: Optional[List[UserObject]] = None
    tags: Optional[List[TagObject]] = None
    recordings: Optional[List[RecordingObject]] = None
    sound_events: Optional[List[SoundEventObject]] = None
    sequences: Optional[List[SequenceObject]] = None
    clips: Optional[List[ClipObject]] = None
    sound_event_predictions: Optional[List[SoundEventPredictionObject]] = None
    sequence_predictions: Optional[List[SequencePredictionObject]] = None
    clip_predictions: Optional[List[ClipPredictionsObject]] = None


class PredictionSetAdapter:
    def __init__(
        self,
        audio_dir: Optional[data.PathLike] = None,
        user_adapter: Optional[UserAdapter] = None,
        tag_adapter: Optional[TagAdapter] = None,
        recording_adapter: Optional[RecordingAdapter] = None,
        note_adapter: Optional[NoteAdapter] = None,
        sound_event_adapter: Optional[SoundEventAdapter] = None,
        sequence_adapter: Optional[SequenceAdapter] = None,
        clip_adapter: Optional[ClipAdapter] = None,
        sound_event_prediction_adapter: Optional[
            SoundEventPredictionAdapter
        ] = None,
        sequence_prediction_adapter: Optional[
            SequencePredictionAdapter
        ] = None,
        clip_predictions_adapter: Optional[ClipPredictionsAdapter] = None,
    ):
        self.user_adapter = user_adapter or UserAdapter()
        self.tag_adapter = tag_adapter or TagAdapter()
        self.note_adapter = note_adapter or NoteAdapter(self.user_adapter)
        self.recording_adapter = recording_adapter or RecordingAdapter(
            self.user_adapter,
            self.tag_adapter,
            self.note_adapter,
            audio_dir=audio_dir,
        )
        self.sound_event_adapter = sound_event_adapter or SoundEventAdapter(
            self.recording_adapter
        )
        self.sequence_adapter = sequence_adapter or SequenceAdapter(
            self.sound_event_adapter,
        )
        self.clip_adapter = clip_adapter or ClipAdapter(self.recording_adapter)
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

    def to_aoef(self, obj: data.PredictionSet) -> PredictionSetObject:
        predictions = [
            self.clip_predictions_adapter.to_aoef(clip_predictions)
            for clip_predictions in obj.clip_predictions
        ]

        return PredictionSetObject(
            uuid=obj.uuid,
            created_on=obj.created_on,
            users=self.user_adapter.values(),
            tags=self.tag_adapter.values(),
            recordings=self.recording_adapter.values(),
            clips=self.clip_adapter.values(),
            sound_events=self.sound_event_adapter.values(),
            sound_event_predictions=self.sound_event_prediction_adapter.values(),
            clip_predictions=predictions,
        )

    def to_soundevent(self, obj: PredictionSetObject) -> data.PredictionSet:
        for tag in obj.tags or []:
            self.tag_adapter.to_soundevent(tag)

        for user in obj.users or []:
            self.user_adapter.to_soundevent(user)

        for recording in obj.recordings or []:
            self.recording_adapter.to_soundevent(recording)

        for sound_event in obj.sound_events or []:
            self.sound_event_adapter.to_soundevent(sound_event)

        for sequence in obj.sequences or []:
            self.sequence_adapter.to_soundevent(sequence)

        for clip in obj.clips or []:
            self.clip_adapter.to_soundevent(clip)

        for sound_event_prediction in obj.sound_event_predictions or []:
            self.sound_event_prediction_adapter.to_soundevent(
                sound_event_prediction
            )

        for sequence_prediction in obj.sequence_predictions or []:
            self.sequence_prediction_adapter.to_soundevent(sequence_prediction)

        clip_predictions = [
            self.clip_predictions_adapter.to_soundevent(clip_predictions)
            for clip_predictions in obj.clip_predictions or []
        ]

        return data.PredictionSet(
            uuid=obj.uuid or uuid4(),
            clip_predictions=clip_predictions,
            created_on=obj.created_on or datetime.datetime.now(),
        )
