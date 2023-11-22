"""Test Suite for AOEF Annotation Task Adapter."""

from soundevent import data
from soundevent.io.aoef.annotation_task import (
    AnnotationTaskAdapter,
    AnnotationTaskObject,
)


def test_annotation_task_can_be_converted_to_aoef(
    annotation_task: data.AnnotationTask,
    annotation_task_adapter: AnnotationTaskAdapter,
):
    obj = annotation_task_adapter.to_aoef(annotation_task)
    assert isinstance(obj, AnnotationTaskObject)


def test_annotation_task_with_status_badge_can_be_recovered(
    annotation_task: data.AnnotationTask,
    annotation_task_adapter: AnnotationTaskAdapter,
):
    obj = annotation_task_adapter.to_aoef(annotation_task)
    recovered = annotation_task_adapter.to_soundevent(obj)
    assert annotation_task == recovered
