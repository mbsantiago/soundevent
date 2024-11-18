"""
# Plotting functions

In this tutorial, we will demonstrate how to plot
audio data and spectrograms using the built-in
plotting functions in `soundevent`.

"""

# %%
# ## Audio Arrays
#
# First lets compute the spectrogram of an audio file.

from soundevent import arrays, audio, data

recording = data.Recording.from_file("sample_audio.wav")
wave = audio.load_recording(recording)
spectrogram = arrays.to_db(
    audio.compute_spectrogram(
        wave,
        window_size=0.064,
        hop_size=0.032,
    )
)

# %%
# Both the wave and spectrogram are [xarray.DataArray][xarray.DataArray]
# objects. Hence we can use the built-in plotting functions to visualize them.

wave.plot()

# %%
# And the spectrogram.

spectrogram.plot()

# %%
# !!! note
#
#     xarray plotting functions are quite flexible and allow you to customize
#     the plot. To see how to use the xarray plotting functions, see the
#     [xarray plotting documentation](https://docs.xarray.dev/en/latest/user-guide/plotting.html).


# %%
# ## Geometries
#
# To plot geometries, we can use the `plot_geometry` function in the
# `soundevent.plot` module.

from soundevent import plot

# %%
# We can plot the different geometries that are defined within `soundevent`.

time_stamp = data.TimeStamp(coordinates=0.1)
time_interval = data.TimeInterval(coordinates=[0.2, 0.3])
point = data.Point(coordinates=[0.4, 6000])
box = data.BoundingBox(coordinates=[0.5, 3000, 0.6, 5000])
line = data.LineString(coordinates=[[0.7, 2000], [0.8, 3000], [0.9, 8000]])
polygon = data.Polygon(
    coordinates=[
        [
            [1.0, 4000],
            [1.1, 5000],
            [1.2, 4000],
            [1.1, 3000],
            [1.0, 4000],
        ]
    ]
)

ax = plot.plot_geometry(time_stamp)
plot.plot_geometry(time_interval, ax=ax, color="red")
plot.plot_geometry(point, ax=ax, color="green")
plot.plot_geometry(box, ax=ax, color="blue")
plot.plot_geometry(line, ax=ax, color="purple", linestyle="--")
plot.plot_geometry(polygon, ax=ax, color="orange")

# %%
# ## Sound Event Annotations
#
# To plot sound event annotations, we can use the `plot_annotation` function in
# the `soundevent.plot` module.

sound_event_annotations = [
    data.SoundEventAnnotation(
        tags=[
            data.Tag(key="animal", value="dog"),
            data.Tag(key="loudness", value="loud"),
        ],
        sound_event=data.SoundEvent(
            recording=recording,
            geometry=data.BoundingBox(coordinates=[0.58, 100, 0.78, 2000]),
        ),
    ),
    data.SoundEventAnnotation(
        tags=[
            data.Tag(key="animal", value="dog"),
            data.Tag(key="loudness", value="loud"),
        ],
        sound_event=data.SoundEvent(
            recording=recording,
            geometry=data.BoundingBox(coordinates=[1.08, 60, 1.34, 1600]),
        ),
    ),
    data.SoundEventAnnotation(
        tags=[
            data.Tag(key="animal", value="dog"),
            data.Tag(key="loudness", value="medium"),
        ],
        sound_event=data.SoundEvent(
            recording=recording,
            geometry=data.BoundingBox(coordinates=[1.52, 30, 1.69, 1400]),
        ),
    ),
    data.SoundEventAnnotation(
        tags=[
            data.Tag(key="animal", value="dog"),
            data.Tag(key="loudness", value="soft"),
        ],
        sound_event=data.SoundEvent(
            recording=recording,
            geometry=data.BoundingBox(coordinates=[1.98, 30, 2.1, 800]),
        ),
    ),
    data.SoundEventAnnotation(
        tags=[
            data.Tag(key="animal", value="dog"),
            data.Tag(key="loudness", value="soft"),
        ],
        sound_event=data.SoundEvent(
            recording=recording,
            geometry=data.BoundingBox(coordinates=[2.45, 30, 2.70, 1300]),
        ),
    ),
]

ax = plot.create_axes()
spectrogram.plot(ax=ax, cmap="gray")

plot.plot_annotations(
    sound_event_annotations,
    ax=ax,
    color="red",
    add_points=False,
    time_offset=0.03,
    freq_offset=300,
)

# %%
# ## Sound Event Predictions

sound_event_predictions = [
    data.SoundEventPrediction(
        score=0.9,
        tags=[
            data.PredictedTag(
                score=0.95, tag=data.Tag(key="animal", value="dog")
            ),
        ],
        sound_event=data.SoundEvent(
            recording=recording,
            geometry=data.BoundingBox(coordinates=[0.58, 100, 0.78, 2000]),
        ),
    ),
    data.SoundEventPrediction(
        score=0.8,
        tags=[
            data.PredictedTag(
                score=0.9, tag=data.Tag(key="animal", value="dog")
            ),
        ],
        sound_event=data.SoundEvent(
            recording=recording,
            geometry=data.BoundingBox(coordinates=[1.08, 60, 1.34, 1600]),
        ),
    ),
    data.SoundEventPrediction(
        score=0.4,
        tags=[
            data.PredictedTag(
                score=0.7, tag=data.Tag(key="animal", value="dog")
            ),
            data.PredictedTag(
                score=0.3, tag=data.Tag(key="animal", value="cat")
            ),
        ],
        sound_event=data.SoundEvent(
            recording=recording,
            geometry=data.BoundingBox(coordinates=[1.52, 30, 1.69, 1400]),
        ),
    ),
    data.SoundEventPrediction(
        score=0.3,
        tags=[
            data.PredictedTag(
                score=0.5, tag=data.Tag(key="animal", value="dog")
            ),
        ],
        sound_event=data.SoundEvent(
            recording=recording,
            geometry=data.BoundingBox(coordinates=[1.98, 30, 2.1, 800]),
        ),
    ),
    data.SoundEventPrediction(
        score=0.8,
        tags=[
            data.PredictedTag(
                score=0.4, tag=data.Tag(key="animal", value="dog")
            ),
        ],
        sound_event=data.SoundEvent(
            recording=recording,
            geometry=data.BoundingBox(coordinates=[2.45, 30, 2.70, 1300]),
        ),
    ),
]

ax = plot.create_axes()
spectrogram.plot(ax=ax, cmap="gray")
plot.plot_predictions(
    sound_event_predictions,
    ax=ax,
    color="red",
    add_points=False,
    time_offset=0.03,
    freq_offset=300,
)
