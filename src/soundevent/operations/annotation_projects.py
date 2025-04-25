from pathlib import Path
from typing import Callable, List, Optional

from soundevent import data
from soundevent.operations.paths import PathTransform
from soundevent.operations.tags import TagTransform


def clean_project_tags(
    project: data.AnnotationProject,
    transform: Callable[[data.Tag], Optional[data.Tag]],
) -> data.AnnotationProject:
    def tag_transform(tags: List[data.Tag]) -> List[data.Tag]:
        new_tags = []
        for tag in tags:
            new_tag = transform(tag)

            if new_tag is None:
                continue

            new_tags.append(new_tag)
        return new_tags

    transformer = TagTransform(tag_transform)
    return transformer.transform_annotation_project(project)


def clean_project_paths(
    project: data.AnnotationProject,
    transform: Callable[[data.PathLike], data.PathLike],
) -> data.AnnotationProject:
    def path_transform(path: Path) -> Path:
        return Path(transform(path))

    transformer = PathTransform(path_transform)
    return transformer.transform_annotation_project(project)
