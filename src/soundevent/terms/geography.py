from soundevent.data import Term

__all__ = [
    "elevation",
    "location_id",
    "country",
    "state_province",
    "county",
]

elevation = Term(
    uri="http://rs.tdwg.org/dwc/terms/verbatimElevation",
    name="dwc:verbatimElevation",
    label="Verbatim Elevation",
    definition="The original description of the elevation (altitude, usually above sea level) of the Location.",
)

location_id = Term(
    uri="http://rs.tdwg.org/dwc/terms/locationID",
    name="dwc:locationID",
    label="Location ID",
    definition="An identifier for the set of location information (data associated with dcterms:Location). May be a global unique identifier or an identifier specific to the data set.",
)

country = Term(
    uri="http://rs.tdwg.org/dwc/terms/country",
    name="dwc:country",
    label="Country",
    definition="The name of the country or major administrative unit in which the Location occurs.",
    scope_note="Recommended best practice is to use a controlled vocabulary such as the Getty Thesaurus of Geographic Names.",
)

state_province = Term(
    uri="http://rs.tdwg.org/dwc/terms/stateProvince",
    name="dwc:stateProvince",
    label="First Order Administrative Division",
    definition="The name of the next smaller administrative region than country (state, province, canton, department, region, etc.) in which the dcterms:Location occurs.",
    scope_note="Recommended best practice is to use a controlled vocabulary such as the Getty Thesaurus of Geographic Names. Recommended best practice is to leave this field blank if the dcterms:Location spans multiple entities at this administrative level or if the dcterms:Location might be in one or another of multiple possible entities at this level. Multiplicity and uncertainty of the geographic entity can be captured either in the term dwc:higherGeography or in the term dwc:locality, or both.",
)

county = Term(
    uri="http://rs.tdwg.org/dwc/terms/county",
    name="dwc:county",
    label="Second Order Division",
    definition="The full, unabbreviated name of the next smaller administrative region than stateProvince (county, shire, department, etc.) in which the dcterms:Location occurs.",
    scope_note="Recommended best practice is to use a controlled vocabulary such as the Getty Thesaurus of Geographic Names. Recommended best practice is to leave this field blank if the dcterms:Location spans multiple entities at this administrative level or if the dcterms:Location might be in one or another of multiple possible entities at this level. Multiplicity and uncertainty of the geographic entity can be captured either in the term dwc:higherGeography or in the term dwc:locality, or both.",
)
