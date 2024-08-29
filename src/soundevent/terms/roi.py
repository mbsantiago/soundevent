from soundevent.data import Term

__all__ = [
    "duration",
    "low_freq",
    "high_freq",
    "bandwidth",
    "num_segments",
]


duration = Term(
    uri="http://rs.tdwg.org/ac/terms/mediaDuration",
    label="Media Duration",
    name="ac:mediaDuration",
    definition="The playback duration of an audio or video file in seconds.",
)

low_freq = Term(
    uri="http://rs.tdwg.org/ac/terms/freqLow",
    label="Lower frequency bound",
    name="ac:freqLow",
    definition="The lowest frequency of the phenomena reflected in the multimedia item or Region of Interest.",
    scope_note="Numeric value in hertz (Hz)",
    description="This term refers to the sound events depicted and not to the constraints of the recording medium, so are in principle independent from sampleRate. If dwc:scientificName is specified and if applied to the entire multimedia item, these frequency bounds refer to the sounds of the species given in the dwc:scientificName throughout the whole recording. Although many users will specify both freqLow and freqHigh, it is permitted to specify just one or the other, for example if only one of the bounds is discernible.",
)

high_freq = Term(
    uri="http://rs.tdwg.org/ac/terms/freqHigh",
    label="Upper frequency bound",
    name="ac:freqHigh",
    definition="The highest frequency of the phenomena reflected in the multimedia item or Region of Interest.",
    scope_note="Numeric value in hertz (Hz)",
    description="This term refers to the sound events depicted and not to the constraints of the recording medium, so are in principle independent from sampleRate. If dwc:scientificName is specified and if applied to the entire multimedia item, these frequency bounds refer to the sounds of the species given in the dwc:scientificName throughout the whole recording. Although many users will specify both freqLow and freqHigh, it is permitted to specify just one or the other, for example if only one of the bounds is discernible.",
)


# TODO: Propose this term to the TDWG Audiovisual Core Task Group
bandwidth = Term(
    name="soundevent:bandwidth",
    label="Bandwidth",
    definition="The difference between the highest and lowest frequency of the sound event.",
    scope_note="Numeric value in hertz (Hz)",
)

num_segments = Term(
    name="soundevent:numSegments",
    label="Number of Segments",
    definition="Number of segments that compose the ROI of a sound event.",
)
