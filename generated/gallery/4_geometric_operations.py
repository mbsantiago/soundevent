"""# Geometric Operations

Sound events are naturally spatial object defined by their location in both
time and frequency. The soundevent's geometry module provides tools to
manipulate the geometry of the sound events, facilitating the analysis of
acoustic data.

???+ info "Usage details"

    To use the `soundevent.geometry` module you need to install some
    additional dependencies. You can do this by running the following
    command:

    ```bash
    pip install soundevent[geometry]
    ```

## Understanding Geometric Operations

Geometric operations provide essential tools to conduct sound event analysis:

1. **Buffering**: Expand sound event boundaries, accommodating uncertainties
inherent in annotations.
2. **Clipping**: Remove unwanted sections.
3. **Spatial Relationships**: Determine overlaps, containment, and distances
between sound events, aiding in comparative analysis.

Here we will explore the geometric operations that can be applied to sound
events and how they can be used to analyze and compare sound events.
"""

from soundevent import data, geometry

geom = data.Polygon(coordinates=[[[1, 2], [4, 3], [5, 6], [1, 2]]])
geom


# %%

buffered = geometry.buffer_geometry(geom, time_buffer=1, freq_buffer=0.5)
buffered

# %%
# ## Datasets
