"""Common types and interfaces within bioacoustic analysis."""

from abc import abstractmethod, ABC
from soundevent import data
from typing import List, Optional


class ClassMapper(ABC):
    """Abstract class for encoding and decoding labels."""

    class_labels: List[str]

    @abstractmethod
    def encode(
        self,
        sound_event_annotation: data.SoundEventAnnotation,
    ) -> Optional[str]:
        pass

    @abstractmethod
    def decode(self, label: str) -> List[data.Tag]:
        pass

    def transform(
        self,
        sound_event_annotation: data.SoundEventAnnotation,
    ) -> Optional[int]:
        class_name = self.encode(sound_event_annotation)

        if class_name not in self.class_labels:
            return None

        return self.class_labels.index(class_name)

    def inverse_transform(self, class_index: int) -> List[data.Tag]:
        if class_index < 0 or class_index >= len(self.class_labels):
            return []

        class_name = self.class_labels[class_index]
        return self.decode(class_name)

    @property
    def num_classes(self) -> int:
        return len(self.class_labels)
