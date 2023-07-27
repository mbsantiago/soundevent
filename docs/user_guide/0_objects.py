"""
# Acoustic Objects

Here we showcase the different objects that are defined
within `soundevent`.
"""

# %%
# ## The data module
#
# All you need to do is import the `data` module from `soundevent`.

from soundevent import data

# %%
# ## Geometries
#
# Here we showcase the different geometries that are defined
# within `soundevent`.
#
# !!! warning
#   All the geometry coordinates should be provided in seconds and Hz.

# %%
# ### TimeStamp
# A `TimeStamp` is defined by a point in time relative to the start of the
# recording.

time_stamp = data.TimeStamp(
    coordinates=0.1,
)
time_stamp

# %%
# ### TimeInterval
# A `TimeInterval` consists of two points in time to mark the start and end of
# an interval.

time_interval = data.TimeInterval(
    coordinates=[0.1, 0.2],
)
time_interval

# %%
# ### Point
# A `Point` is a point in time and frequency.

point = data.Point(
    coordinates=[0.1, 2000],
)
point

# %%
# ### BoundingBox

box = data.BoundingBox(
    coordinates=[0.1, 2000, 0.2, 3000],
)
box

# %%
# A `LineString` is a sequence of points that are connected by a line.

line = data.LineString(
    coordinates=[[0.1, 2000], [0.2, 4000]],
)
line

# %%
# A `Polygon`

polygon = data.Polygon(
    coordinates=[
        [
            [0.1, 2000],
            [0.2, 3000],
            [0.3, 2000],
            [0.2, 1000],
            [0.1, 2000],
        ],
        [
            [0.15, 2000],
            [0.25, 2000],
            [0.2, 1500],
            [0.15, 2000],
        ],
    ],
)
polygon


# %%
# ## Geometry functions
#
# You can buffer geometries in time and frequency.

from soundevent import geometry

buffer = geometry.buffer_geometry(
    polygon,
    time_buffer=0.01,
    freq_buffer=100,
)
buffer
