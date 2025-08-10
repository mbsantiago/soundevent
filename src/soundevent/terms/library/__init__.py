from soundevent.data import Term
from soundevent.terms.io import TermSet, register_term_set
from soundevent.terms.library.devices import capture_device
from soundevent.terms.library.geography import (
    country,
    county,
    elevation,
    location_id,
    state_province,
)
from soundevent.terms.library.metrics import (
    accuracy,
    average_precision,
    balanced_accuracy,
    f1_score,
    jaccard_index,
    mean_average_precision,
    top_3_accuracy,
    true_class_probability,
)
from soundevent.terms.library.roi import (
    bandwidth,
    duration,
    high_freq,
    low_freq,
    num_segments,
)
from soundevent.terms.library.taxonomy import (
    common_name,
    family,
    genus,
    order,
    scientific_name,
    taxonomic_class,
)

alternative = Term(
    uri="http://purl.org/dc/terms/alternative",
    name="dcterms:alternative",
    label="Alternative",
    definition="An alternative name for the resource.",
    scope_note="Can be used to reference an identifier from an external source for a resource within a new collection, acting as a cross-reference.",
)


soundevent_term_set = TermSet(
    terms=[
        accuracy,
        alternative,
        average_precision,
        balanced_accuracy,
        bandwidth,
        capture_device,
        common_name,
        country,
        county,
        duration,
        elevation,
        f1_score,
        family,
        genus,
        high_freq,
        jaccard_index,
        location_id,
        low_freq,
        mean_average_precision,
        num_segments,
        order,
        scientific_name,
        state_province,
        taxonomic_class,
        top_3_accuracy,
        true_class_probability,
    ],
    aliases={
        "species": scientific_name.name,
        "genus": genus.name,
        "family": family.name,
        "order": order.name,
        "common_name": common_name.name,
        "class": taxonomic_class.name,
        "duration": duration.name,
        "low_freq": low_freq.name,
        "high_freq": high_freq.name,
        "location_id": location_id.name,
        "site_id": location_id.name,
        "country": country.name,
        "state": state_province.name,
    },
)

register_term_set(soundevent_term_set)

__all__ = [
    "accuracy",
    "alternative",
    "average_precision",
    "balanced_accuracy",
    "bandwidth",
    "capture_device",
    "common_name",
    "country",
    "county",
    "duration",
    "elevation",
    "f1_score",
    "family",
    "genus",
    "high_freq",
    "jaccard_index",
    "location_id",
    "low_freq",
    "mean_average_precision",
    "num_segments",
    "order",
    "scientific_name",
    "state_province",
    "taxonomic_class",
    "top_3_accuracy",
    "true_class_probability",
]
