"""Measures of affinity between Sound Events."""

import sys
from typing import Generic

from soundevent import data

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec


P = ParamSpec("P")


class AffinityFunction(Protocol, Generic[P]):
    """Protocol for defining an affinity function between two geometries.

    An affinity function is a function that measures the similarity or affinity
    between two geometries. This protocol defines the structure and
    requirements for implementing an affinity function in the `soundevent`
    package.

    The affinity function should be a callable that takes two geometries as
    input and returns a float value representing the affinity between them. The
    function should accept any type of geometry as input, allowing for
    flexibility in the types of geometries that can be compared. The affinity
    value should indicate the degree of similarity between the two geometries,
    with higher values indicating greater similarity.

    """

    def __call__(
        self,
        geometry1: data.Geometry,
        geometry2: data.Geometry,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> float:
        """Compute the affinity between two geometries.

        Parameters
        ----------
        geometry1 : data.Geometry
            The first geometry.
        geometry2 : data.Geometry
            The second geometry.
        **kwargs
            Additional keyword arguments for customization.

        Returns
        -------
        affinity : float
            The computed affinity between the two geometries.

        """
        ...


# def iou(
#     geometry1: data.Geometry,
#     geometry2: data.Geometry,
#     freq_buffer: float = 0,
#     time_buffer: float = 0,
# ) -> float:
#     """Measure the Intersection over Union between two geometries.
#
#     Parameters
#     ----------
#     geometry1 : data.Geometry
#         The first geometry.
#
#     geometry2 : data.Geometry
#         The second geometry.
#
#     freq_buffer : float, optional
#         The frequency buffer to apply to the geometries, in Hz.
#         Defaults to 0.
#
#     time_buffer : float, optional
#         The time buffer to apply to the geometries, in seconds.
#         Defaults to 0.
#
#     Returns
#     -------
#     affinity : float
#         The Intersection over Union between the two geometries.
#     """


# func: AffinityFunction = iou
