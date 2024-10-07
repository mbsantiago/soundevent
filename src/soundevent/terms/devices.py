from soundevent.data import Term

__all__ = [
    "capture_device",
]

capture_device = Term(
    uri="http://rs.tdwg.org/ac/terms/captureDevice",
    name="ac:captureDevice",
    label="Capture Device",
    definition="Free form text describing the device or devices used to create the resource.",
    scope_note='It is best practice to record the device; this may include a combination such as camera plus lens, or camera plus microscope. Examples: "Canon Supershot 2000", "Makroscan Scanner 2000", "Zeiss Axioscope with Camera IIIu", "SEM (Scanning Electron Microscope)".',
)
