from soundevent.data import Term

__all__ = [
    "scientific_name",
    "common_name",
    "family",
    "genus",
    "order",
]

scientific_name = Term(
    uri="http://rs.tdwg.org/dwc/terms/scientificName",
    name="dwc:scientificName",
    label="Scientific Taxon Name",
    definition="The full scientific name, with authorship and date information if known. When forming part of an Identification, this should be the name in lowest level taxonomic rank that can be determined. This term should not contain identification qualifications, which should instead be supplied in the IdentificationQualifier term.",
    scope_note="Scientific names of taxa represented in the media resource (with date and name authorship information if available) of the lowest level taxonomic rank that can be applied.",
    description='The Scientific Taxon Name may possibly be of a higher rank, e.g., a genus or family name, if this is the most specific identification available. Where multiple taxa are the subject of the media item, multiple names may be given. If possible, add this information here even if the title or caption of the resource already contains scientific taxon names. Where the list of scientific taxon names is impractically large (e.g., media collections or identification tools), the number of taxa should be given in Taxon Count (see below). If possible, avoid repeating the Taxonomic Coverage here. Do not use abbreviated Genus names ("P. vulgaris"). It is recommended to provide author citation to scientific names, to avoid ambiguities in the presence of homonyms (the same name created by different authors for different taxa). Identifier qualifications should be supplied in the Identification Qualifier term rather than here (i. e. "Abies cf. alba" is deprecated, to be replaced with Scientific Taxon Name = "Abies alba" and Identification Qualifier = "cf. species")',
)

common_name = Term(
    uri="http://rs.tdwg.org/dwc/terms/vernacularName",
    name="dwc:vernacularName",
    label="Common Name",
    definition="A common or vernacular name.",
    scope_note="Common (= vernacular) names of the subject in one or several languages. The ISO 639-1 language code SHOULD be given in parentheses after the name if not all names are given by values of the Metadata Language term.",
    description="The ISO language code after the name should be formatted as in the following example: 'abete bianco (it); Tanne (de); White Fir (en)'. If names are known to be male- or female-specific, this may be specified as in: 'ewe (en-female); ram (en-male);'.",
)

order = Term(
    uri="http://rs.tdwg.org/dwc/terms/order",
    name="dwc:order",
    label="Order",
    definition="The full scientific name of the order in which the dwc:Taxon is classified.",
)

family = Term(
    uri="http://rs.tdwg.org/dwc/terms/family",
    name="dwc:family",
    label="Family",
    definition="The full scientific name of the family in which the dwc:Taxon is classified.",
)

genus = Term(
    uri="http://rs.tdwg.org/dwc/terms/genus",
    name="dwc:genus",
    label="Genus",
    definition="The full scientific name of the genus in which the dwc:Taxon is classified.",
)

taxonomic_class = Term(
    uri="http://rs.tdwg.org/dwc/terms/class",
    name="dwc:class",
    label="Class",
    definition="The full scientific name of the class in which the dwc:Taxon is classified.",
)
