"""Features.

Features are numerical values that can be associated with sound
events, clips, and recordings. They provide additional information and
metadata, enriching the objects they are attached to. Features play a
crucial role in searching, organizing, and analyzing bioacoustic data.
Each feature consists of a name that describes the characteristic it
represents, and a corresponding numeric value that quantifies the
feature.

* Sound Events: Features attached to sound events offer various types
of information. They can provide basic characteristics, such as
duration or bandwidth, which give a general description of the sound
event. Additionally, features can capture more intricate details that
are extracted using deep learning models. These details might include
specific temporal or spectral properties of the sound event, aiding in
fine-grained analysis and classification.

* Clips: Features associated with clips describe the acoustic content
of the entire soundscape within the clip. They offer insights into the
overall characteristics of the audio, beyond individual sound events.
Examples of clip-level features include signal-to-noise ratio,
acoustic indices, or other statistical measures that summarize the
properties of the sound within the clip.

* Recordings: Features can also be attached to recordings, providing
contextual information of a numeric nature. These features offer
additional metadata about the recording session, such as the
temperature, wind speed, or other environmental conditions at the time
of recording. They can also include characteristics of the recording
device, such as the height of the recorder or other relevant
parameters.

## Exploring and Analyzing Annotations:

By having multiple features attached to sound events, clips, and
recordings, users gain the ability to explore and analyze their
data more comprehensively. Features allow for the identification
of outliers, understanding the distribution of specific
characteristics across a collection of sound events, and
conducting statistical analyses on the annotated dataset.
"""

from pydantic import BaseModel

__all__ = [
    "Feature",
]


class Feature(BaseModel):
    """Feature."""

    name: str
    """The name of the feature."""

    value: float
    """The numeric value of the feature."""

    def __hash__(self):
        """Hash the Feature object."""
        return hash((self.name, self.value))
