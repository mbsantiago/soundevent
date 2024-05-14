"""Common types and interfaces within bioacoustic analysis."""

from abc import ABC, abstractmethod
from typing import List, Optional

from soundevent import data


class Model(ABC):
    """Abstract class for bioacoustic models."""

    @abstractmethod
    def predict(self, clip: data.Clip, **kwargs) -> data.ClipPrediction:
        """Predict sound events in a clip.

        Parameters
        ----------
        clip : data.Clip
            A clip data object.
        **kwargs
            Additional keyword arguments.

        Returns
        -------
        data.ClipPrediction
            A clip prediction object.
        """
        ...


class ClassMapper(ABC):
    """Abstract class for encoding and decoding labels."""

    class_labels: List[str]

    @abstractmethod
    def encode(
        self,
        sound_event_annotation: data.SoundEventAnnotation,
    ) -> Optional[str]:
        """Encode a sound event annotation into a class label.

        The user should implement this method to encode a sound event annotation
        into a class label. If the sound event annotation does not have a class
        label, the method should return None. This is helpful in case
        the user wants to ignore some sound event annotations.
        """
        pass

    @abstractmethod
    def decode(self, label: str) -> List[data.Tag]:
        """Decode a class label into a list of tags.

        The user should implement this method to decode a class label into a
        list of tags. This is helpful when the user wants to convert a class
        label into a list of tags to reconstruct the sound event annotation.
        """
        pass

    def transform(
        self,
        sound_event_annotation: data.SoundEventAnnotation,
    ) -> Optional[int]:
        """Transform a sound event annotation into a class index.

        Parameters
        ----------
        sound_event_annotation : data.SoundEventAnnotation
            A sound event annotation.

        Returns
        -------
        Optional[int]
            The class index of the sound event annotation.
            If no class is provided, returns None.
        """
        class_name = self.encode(sound_event_annotation)

        if class_name not in self.class_labels:
            return None

        return self.class_labels.index(class_name)

    def inverse_transform(self, class_index: int) -> List[data.Tag]:
        """Inverse transform a class index into a list of tags.

        Parameters
        ----------
        class_index : int
            The class index.

        Returns
        -------
        List[data.Tag]
            A list of tags that represent the class index.
        """
        if class_index < 0 or class_index >= len(self.class_labels):
            return []

        class_name = self.class_labels[class_index]
        return self.decode(class_name)

    @property
    def num_classes(self) -> int:
        """Return the number of classes."""
        return len(self.class_labels)
