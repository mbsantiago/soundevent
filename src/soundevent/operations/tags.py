from typing import Callable, List

from soundevent import data

__all__ = [
    "TagTransform",
]


class TagTransform:
    def __init__(
        self,
        tag_transform: Callable[[List[data.Tag]], List[data.Tag]],
    ):
        self.tag_transform = tag_transform

    def transform_tags(self, tags: List[data.Tag]) -> List[data.Tag]:
        return self.tag_transform(tags)

    def transform_recording(self, recording: data.Recording) -> data.Recording:
        return recording.model_copy(
            update=dict(tags=self.transform_tags(recording.tags))
        )

    def transform_sound_event(
        self, sound_event: data.SoundEvent
    ) -> data.SoundEvent:
        return sound_event.model_copy(
            update=dict(
                recording=self.transform_recording(sound_event.recording)
            )
        )

    def transform_sound_event_annotation(
        self,
        sound_event_annotation: data.SoundEventAnnotation,
    ) -> data.SoundEventAnnotation:
        return sound_event_annotation.model_copy(
            update=dict(
                tags=self.transform_tags(sound_event_annotation.tags),
                sound_event=self.transform_sound_event(
                    sound_event_annotation.sound_event
                ),
            )
        )

    def transform_clip(self, clip: data.Clip) -> data.Clip:
        return clip.model_copy(
            update=dict(recording=self.transform_recording(clip.recording))
        )

    def transform_clip_annotation(
        self,
        clip_annotation: data.ClipAnnotation,
    ) -> data.ClipAnnotation:
        return clip_annotation.model_copy(
            update=dict(
                tags=self.transform_tags(clip_annotation.tags),
                clip=self.transform_clip(clip_annotation.clip),
                sound_events=[
                    self.transform_sound_event_annotation(sound_event)
                    for sound_event in clip_annotation.sound_events
                ],
            )
        )

    def transform_annotation_task(
        self,
        annotation_task: data.AnnotationTask,
    ) -> data.AnnotationTask:
        return annotation_task.model_copy(
            update=dict(clip=self.transform_clip(annotation_task.clip))
        )

    def transform_dataset(self, dataset: data.Dataset) -> data.Dataset:
        return dataset.model_copy(
            update=dict(
                recordings=[
                    self.transform_recording(recording)
                    for recording in dataset.recordings
                ]
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
                tasks=[
                    self.transform_annotation_task(annotation_task)
                    for annotation_task in annotation_project.tasks
                ],
            ),
        )
