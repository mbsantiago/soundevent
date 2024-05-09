"""Standard attributes for acoustic data arrays.

This module provides enumerations for commonly used attributes to describe
dimensions and arrays of numerical data in computational acoustics tasks.
These attributes are based on a subset of the Climate and Forecast (CF)
conventions [documentation](https://cfconventions.org/), a widely used
standard for describing scientific data.

The module includes enums for:

* Dimension attributes
* Range attributes
* Array attributes

By using these standard attributes, you can ensure interoperability and
consistency in your acoustic data representation.

For a complete list of CF conventions attributes, refer to the
[Attribute Conventions](https://cfconventions.org/Data/cf-conventions/cf-conventions-1.11/cf-conventions.html#attribute-appendix).
"""

from enum import Enum

__all__ = [
    "DimAttrs",
    "ArrayAttrs",
]


class DimAttrs(str, Enum):
    """Standard attribute names for acoustic data dimensions.

    This enumeration defines standard attribute names used to describe
    dimensions of acoustic data arrays. These attributes follow the CF
    conventions and provide a consistent way to represent information about
    dimensions, such as units, standard names, and long names.
    """

    units = "units"
    """ Attribute name for the units of a dimension. 

    This specifies the physical quantity represented by the dimension, such as
    'seconds' for time or 'meters' for distance. It follows the UDUNITS
    standard for unit symbols.
    """

    standard_name = "standard_name"
    """Attribute name for the standard name of a dimension.

    As defined by the CF conventions. This provides a consistent way to
    identify dimensions across different datasets.
    """

    long_name = "long_name"
    """Attribute name for a human-readable description of the dimension.

    This can be more detailed than the standard name and provide additional
    context for users.
    """

    step = "step"
    """Attribute name for the step size of a range dimension. 

    Specifies the distance between consecutive values in the range, which might
    not be explicitly stored as a coordinate value. If not present, the
    dimension is assumed to be irregularly spaced. Not a standard CF attribute.
    """


class ArrayAttrs(str, Enum):
    """Standard attribute names for acoustic data arrays.

    This enumeration defines standard attribute names used to describe
    properties of acoustic data arrays. These attributes follow the CF
    conventions and provide a consistent way to represent information about the
    data.
    """

    units = "units"
    """Attribute name for the units of an array variable.

     This specifies the physical quantity represented by the array, such as
     'dB' for sound pressure level or 'meters' for distance. It follows the
     UDUNITS standard for unit symbols.
    """

    standard_name = "standard_name"
    """Attribute name for the standard name of an array variable.

    As defined by the CF conventions. This provides a consistent way to
    identify arrays across different datasets.
    """

    long_name = "long_name"
    """Attribute name for a human-readable description of the array variable.

    This can be more detailed than the standard name and provide additional
    context for users.
    """

    comment = "comment"
    """Attribute name for any additional comments or explanations about the
    array variable.
    """

    references = "references"
    """Attribute name for references to external documentation or resources
    that provide more information about the array variable.
    """
