"""Test suite for AOEF Annotation Project Adapter."""

from soundevent import data
from soundevent.io.aoef.annotation_project import (
    AnnotationProjectAdapter,
    AnnotationProjectObject,
)


def test_annotation_project_can_be_converted_to_aoef(
    annotation_project: data.AnnotationProject,
    annotation_project_adapter: AnnotationProjectAdapter,
):
    obj = annotation_project_adapter.to_aoef(annotation_project)
    assert isinstance(obj, AnnotationProjectObject)


def test_annotation_project_can_be_recovered(
    annotation_project: data.AnnotationProject,
    annotation_project_adapter: AnnotationProjectAdapter,
):
    obj = annotation_project_adapter.to_aoef(annotation_project)
    recovered = annotation_project_adapter.to_soundevent(obj)
    assert annotation_project == recovered
