"""Base classes for data transformations."""

from collections.abc import Sequence
from pathlib import Path

from soundevent import data


class TransformBase:
    """Base class for creating data transformations.

    This class implements the visitor pattern to traverse the complex hierarchy
    of soundevent data objects. It provides `transform_*` methods for each type
    of data object in the soundevent ecosystem.

    The default implementation of each `transform_*` method returns the object
    unchanged or, for container-like objects, recursively calls the appropriate
    transform methods on their children and returns a new container with the
    transformed children.

    To create a custom transformation, inherit from this class and override the
    `transform_*` method for the specific object or attribute you want to
    modify.

    Examples
    --------
    >>> from soundevent import data
    >>> from soundevent.transforms.base import TransformBase
    >>>
    >>> class UserAnonymizer(TransformBase):
    ...     def transform_user(self, user: data.User) -> data.User:
    ...         return user.model_copy(update={"name": "anonymous"})

    """

    def transform_path(self, path: Path) -> Path:
        return path

    def transform_geometry(self, geometry: data.Geometry) -> data.Geometry:
        return geometry

    def transform_user(self, user: data.User) -> data.User:
        return user

    def transform_notes(
        self, notes: Sequence[data.Note]
    ) -> Sequence[data.Note]:
        return notes

    def transform_features(
        self, features: Sequence[data.Feature]
    ) -> Sequence[data.Feature]:
        return features

    def transform_tags(self, tags: Sequence[data.Tag]) -> Sequence[data.Tag]:
        return tags

    def transform_predicted_tags(
        self,
        predicted_tags: Sequence[data.PredictedTag],
    ) -> Sequence[data.PredictedTag]:
        return predicted_tags

    def transform_recording(self, recording: data.Recording) -> data.Recording:
        return recording.model_copy(
            update=dict(
                owners=[
                    self.transform_user(user) for user in recording.owners
                ],
                path=self.transform_path(recording.path),
                tags=self.transform_tags(recording.tags),
                features=self.transform_features(recording.features),
                notes=self.transform_notes(recording.notes),
            )
        )

    def transform_clip(self, clip: data.Clip) -> data.Clip:
        return clip.model_copy(
            update=dict(
                recording=self.transform_recording(clip.recording),
                features=self.transform_features(clip.features),
            ),
        )

    def transform_sound_event(
        self, sound_event: data.SoundEvent
    ) -> data.SoundEvent:
        return sound_event.model_copy(
            update=dict(
                geometry=self.transform_geometry(sound_event.geometry)
                if sound_event.geometry is not None
                else None,
                recording=self.transform_recording(sound_event.recording),
                features=self.transform_features(sound_event.features),
            )
        )

    def transform_sound_event_annotation(
        self,
        sound_event_annotation: data.SoundEventAnnotation,
    ) -> data.SoundEventAnnotation:
        return sound_event_annotation.model_copy(
            update=dict(
                sound_event=self.transform_sound_event(
                    sound_event_annotation.sound_event
                ),
                notes=self.transform_notes(sound_event_annotation.notes),
                tags=self.transform_tags(sound_event_annotation.tags),
                created_by=self.transform_user(
                    sound_event_annotation.created_by
                )
                if sound_event_annotation.created_by is not None
                else None,
            )
        )

    def transform_sequence_annotation(
        self, sequence_annotation: data.SequenceAnnotation
    ) -> data.SequenceAnnotation:
        return sequence_annotation.model_copy(
            update=dict(
                sequence=self.transform_sequence(sequence_annotation.sequence),
                tags=self.transform_tags(sequence_annotation.tags),
                created_by=self.transform_user(sequence_annotation.created_by)
                if sequence_annotation.created_by is not None
                else None,
                notes=self.transform_notes(sequence_annotation.notes),
            )
        )

    def transform_clip_annotation(
        self, clip_annotation: data.ClipAnnotation
    ) -> data.ClipAnnotation:
        return clip_annotation.model_copy(
            update=dict(
                clip=self.transform_clip(clip_annotation.clip),
                sound_events=[
                    self.transform_sound_event_annotation(sound_event)
                    for sound_event in clip_annotation.sound_events
                ],
                tags=self.transform_tags(clip_annotation.tags),
                sequences=[
                    self.transform_sequence_annotation(sequence)
                    for sequence in clip_annotation.sequences
                ],
                notes=self.transform_notes(clip_annotation.notes),
            )
        )

    def transform_status_badge(
        self, status_badge: data.StatusBadge
    ) -> data.StatusBadge:
        return status_badge.model_copy(
            update=dict(
                owner=self.transform_user(status_badge.owner)
                if status_badge.owner is not None
                else None
            )
        )

    def transform_annotation_task(self, annotation_task: data.AnnotationTask):
        return annotation_task.model_copy(
            update=dict(
                clip=self.transform_clip(annotation_task.clip),
                status_badges=[
                    self.transform_status_badge(status_badge)
                    for status_badge in annotation_task.status_badges
                ],
            )
        )

    def transform_recording_set(
        self,
        recording_set: data.RecordingSet,
    ) -> data.RecordingSet:
        return recording_set.model_copy(
            update=dict(
                recordings=[
                    self.transform_recording(recording)
                    for recording in recording_set.recordings
                ]
            )
        )

    def transform_sequence(self, sequence: data.Sequence) -> data.Sequence:
        return sequence.model_copy(
            update=dict(
                sound_events=[
                    self.transform_sound_event(sound_event)
                    for sound_event in sequence.sound_events
                ],
                features=self.transform_features(sequence.features),
                parent=self.transform_sequence(sequence.parent)
                if sequence.parent is not None
                else None,
            )
        )

    def transform_sound_event_prediction(
        self,
        sound_event_prediction: data.SoundEventPrediction,
    ) -> data.SoundEventPrediction:
        return sound_event_prediction.model_copy(
            update=dict(
                sound_event=self.transform_sound_event(
                    sound_event_prediction.sound_event
                ),
                tags=self.transform_predicted_tags(
                    sound_event_prediction.tags
                ),
            )
        )

    def transform_sequence_prediction(
        self,
        sequence_prediction: data.SequencePrediction,
    ) -> data.SequencePrediction:
        return sequence_prediction.model_copy(
            update=dict(
                sequence=self.transform_sequence(sequence_prediction.sequence),
                tags=self.transform_predicted_tags(sequence_prediction.tags),
            )
        )

    def transform_clip_prediction(
        self, clip_prediction: data.ClipPrediction
    ) -> data.ClipPrediction:
        return clip_prediction.model_copy(
            update=dict(
                clip=self.transform_clip(clip_prediction.clip),
                tags=self.transform_predicted_tags(clip_prediction.tags),
                sound_events=[
                    self.transform_sound_event_prediction(sound_event)
                    for sound_event in clip_prediction.sound_events
                ],
                sequences=[
                    self.transform_sequence_prediction(sequence)
                    for sequence in clip_prediction.sequences
                ],
                features=self.transform_features(clip_prediction.features),
            )
        )

    def transform_dataset(
        self,
        dataset: data.Dataset,
    ) -> data.Dataset:
        return dataset.model_copy(
            update=dict(
                recordings=[
                    self.transform_recording(recording)
                    for recording in dataset.recordings
                ]
            )
        )

    def transform_annotation_set(
        self,
        annotation_set: data.AnnotationSet,
    ) -> data.AnnotationSet:
        return annotation_set.model_copy(
            update=dict(
                clip_annotations=[
                    self.transform_clip_annotation(clip_annotation)
                    for clip_annotation in annotation_set.clip_annotations
                ],
            )
        )

    def transform_annotation_project(
        self,
        annotation_project: data.AnnotationProject,
    ) -> data.AnnotationProject:
        return annotation_project.model_copy(
            update=dict(
                clip_annotations=[
                    self.transform_clip_annotation(clip_annotation)
                    for clip_annotation in annotation_project.clip_annotations
                ],
                annotation_tags=self.transform_tags(
                    annotation_project.annotation_tags
                ),
                tasks=[
                    self.transform_annotation_task(task)
                    for task in annotation_project.tasks
                ],
            )
        )

    def transform_evaluation_set(
        self, evaluation_set: data.EvaluationSet
    ) -> data.EvaluationSet:
        return evaluation_set.model_copy(
            update=dict(
                clip_annotations=[
                    self.transform_clip_annotation(clip_annotation)
                    for clip_annotation in evaluation_set.clip_annotations
                ],
                evaluation_tags=self.transform_tags(
                    evaluation_set.evaluation_tags
                ),
            )
        )

    def transform_prediction_set(
        self, prediction_set: data.PredictionSet
    ) -> data.PredictionSet:
        return prediction_set.model_copy(
            update=dict(
                clip_predictions=[
                    self.transform_clip_prediction(clip_prediction)
                    for clip_prediction in prediction_set.clip_predictions
                ]
            )
        )

    def transform_model_run(self, model_run: data.ModelRun) -> data.ModelRun:
        return model_run.model_copy(
            update=dict(
                clip_predictions=[
                    self.transform_clip_prediction(clip_prediction)
                    for clip_prediction in model_run.clip_predictions
                ]
            )
        )
