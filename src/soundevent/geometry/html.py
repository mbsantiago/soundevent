"""HTML representation of geometries."""

import shapely

from soundevent import data
from soundevent.geometry.conversion import geometry_to_shapely


def timestamp_to_html(geom: data.TimeStamp) -> str:
    """Represent the geometry as HTML.

    Returns
    -------
    str
        The HTML representation of the geometry.
    """
    time = geom.coordinates

    label_style = "; ".join(
        [
            "position: absolute",
            "bottom: 0",
            "transform: translate(0, 100%)",
        ]
    )

    inner_style = "; ".join(
        [
            "display: inline",
            "vertical-align: bottom",
        ]
    )

    style = "; ".join(
        [
            "display: inline-block",
            "position: relative",
            "width: 100px",
            "height: 100px",
        ]
    )

    shp_geom = geometry_to_shapely(geom)
    geom_svg = shp_geom._repr_svg_()

    return (
        f'<div style="{style}">'
        f'<div style="{label_style}">'
        f'<small style="{inner_style}">{time}</small>'
        "</div>"
        f"{geom_svg}"
        "</div>"
    )


def shapely_to_html(geometry: shapely.Geometry) -> str:
    """Represent the geometry as HTML.

    Returns
    -------
    str
        The HTML representation of the geometry.
    """
    start_time, low_freq, end_time, high_freq = shapely.bounds(geometry)

    duration = end_time - start_time
    bandwidth = high_freq - low_freq

    factor = [
        1 / duration if duration > 0 else 1,
        1 / bandwidth if bandwidth > 0 else 1,
    ]

    transformed = shapely.transform(
        geometry,
        lambda x: x * factor,
    )

    style = (
        "display: inline-block; "
        "position: relative;"
        "width: 100px; "
        "height: 100px; "
    )

    def axis_label(
        label: float,
        top: bool = False,
        left: bool = True,
        axis: str = "time",
    ) -> str:
        outer_style = "; ".join(
            [
                "position: absolute",
                "top: 0; " if top else "bottom: 0",
                "left: 0; " if left else "right: 0",
                (
                    "transform: translate(-105%, 0)"
                    if axis == "freq"
                    else "transform: translate(0, 100%)"
                ),
            ]
        )

        inner_style = "; ".join(
            [
                "display: inline",
                (
                    "vertical-align: top"
                    if axis == "time"
                    else "vertical-align: bottom"
                ),
            ]
        )

        label_str = f"{label:.2f}" if axis == "time" else f"{label:.0f}"

        return (
            f'<div style="{outer_style}">'
            f'<small style="{inner_style}">{label_str}</small>'
            "</div>"
        )

    return (
        f'<div style="{style}">'
        f'{axis_label(start_time, left=True, axis="time")}'
        f'{axis_label(end_time, left=False, axis="time")}'
        f'{axis_label(low_freq, top=False, axis="freq")}'
        f'{axis_label(high_freq, top=True, axis="freq")}'
        f"{transformed}"
        "</div>"
    )


def geometry_to_html(geom: data.Geometry) -> str:
    """Represent the geometry as HTML.

    Parameters
    ----------
    geom : data.Geometry
        The geometry to represent as HTML.

    Returns
    -------
    str
        The HTML representation of the geometry.
    """
    if geom.type == "TimeStamp":
        return timestamp_to_html(geom)
    else:
        return shapely_to_html(geometry_to_shapely(geom))
