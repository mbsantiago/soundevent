"""# Integrating Crowsetta with Soundevent

[Crowsetta](https://crowsetta.readthedocs.io/en/latest/) is a versatile Python
tool designed for handling annotations of animal vocalizations and bioacoustics
data. If you're working with diverse annotation formats Crowsetta has you
covered. Soundevent complements this functionality with its
`soundevent.io.crowsetta` module, offering a convenient solution for converting
between Crowsetta and Soundevent formats.

In this guide, we'll walk through the process of using Crowsetta to load
annotations and then converting them to Soundevent format using the
[`soundevent.io.crowsetta`][soundevent.io.crowsetta] module.

???+ info "Usage details"

    To use the `soundevent.io.crowsetta` module you need to install some
    additional dependencies. You can do this by running the following
    command:

    ```bash
    pip install soundevent[crowsetta]
    ```

## Loading annotations with `crowsetta`

To begin our journey, let's delve into loading annotations using Crowsetta.

### Crowsetta supported formats

Crowsetta offers support for various annotation formats. Let's explore the
available formats:

"""

import crowsetta

print(crowsetta.data.available_formats())

# %%
# ### Loading Example Raven Annotations
#
# Let's walk through the process of loading example Raven annotations using
# Crowsetta.

import os
import tempfile

with tempfile.TemporaryDirectory() as tmpdirname:
    # Extract the example data files to a temporary directory
    data_dir = os.path.join(tmpdirname, "crowsetta_data")
    crowsetta.data.extract_data_files(user_data_dir=data_dir)

    # Select a Raven example file
    example_file = crowsetta.data.get("raven", user_data_dir=data_dir)

    # Create a Raven transcriber
    transcriber = crowsetta.Transcriber("raven")

    # Load the Raven annotations
    # For this example, we assume the annotations correspond to a test audio
    # file.
    raven_annotations = transcriber.from_file(
        example_file.annot_path,
        annot_col="Species",
        audio_path="sample_audio.wav",
    )

    print(raven_annotations)

    # Convert the annotations to the standard crowsetta format
    annotations = raven_annotations.to_annot()

print(f"Citation: {example_file.citation}")
print(f"Loaded {len(annotations.bboxes)} bounding box annotations")
print("Notated file: ", annotations.notated_path)

# %%
# ## Converting to Soundevent format
#
# Having successfully loaded the annotations using Crowsetta, we're now ready
# to convert them to Soundevent format.

import soundevent.io.crowsetta as cr

# Convert Crowsetta Annotations to Soundevent ClipAnnotation
clip_annotation = cr.annotation_to_clip_annotation(annotations)

# Print JSON representation of the ClipAnnotation object
print(
    clip_annotation.model_dump_json(
        indent=2,
        # Avoid printing irrelevant information
        exclude_none=True,
        exclude_defaults=True,
        exclude_unset=True,
    )
)

# %%
# And that's it! We have successfully loaded annotations using `crowsetta` and
# converted them to `soundevent` format.

# %%
# ## Converting back to `crowsetta` format
#
# Now, let's explore the process of converting Soundevent annotations back to
# Crowsetta objects.

from soundevent.data import (
    BoundingBox,
    Clip,
    ClipAnnotation,
    Recording,
    SoundEvent,
    SoundEventAnnotation,
    Tag,
)

# First, let's create some annotations for the example audio file
recording = Recording.from_file("sample_audio.wav")

clip_annotation = ClipAnnotation(
    clip=Clip(
        recording=recording,
        start_time=0,
        end_time=1,
    ),
    sound_events=[
        SoundEventAnnotation(
            tags=[
                Tag(key="species", value="bird"),
                Tag(key="color", value="red"),
            ],
            sound_event=SoundEvent(
                recording=recording,
                geometry=BoundingBox(coordinates=[0.1, 2000, 0.2, 3000]),
            ),
        ),
        SoundEventAnnotation(
            tags=[Tag(key="species", value="frog")],
            sound_event=SoundEvent(
                recording=recording,
                geometry=BoundingBox(coordinates=[0.3, 1000, 0.6, 1500]),
            ),
        ),
    ],
)

# %%
# Now, let's convert the ClipAnnotation object to Crowsetta format

annotations = cr.annotation_from_clip_annotation(
    clip_annotation,
    "random_file_path.txt",
    annotation_fmt="bbox",
)

print(annotations)

# %%
# !!! note
#
#     While working with `crowsetta`, annotation objects are typically loaded
#     from a file. In this demonstration, we're using a random file name to
#     instantiate the annotations, even though the file doesn't exist. It's
#     important to note that `crowsetta` requires a file path to create
#     annotations, even if they are not actually written to the file.
#     Therefore, using a random filepath is a safe practice.

# %%
# ## Finer Control
#
# When converting between crowsetta and soundevent formats, you have a
# multitude of options at your disposal. Soundevent objects can contain a
# wealth of information beyond what crowsetta objects offer, including multiple
# tags, notes, various geometry types, and more. Consequently, the conversion
# process isn't always straightforward. Particularly when converting from
# soundevent to crowsetta format, you'll need to make decisions regarding how
# to handle the additional information.

# %%
# ### Tags and Labels
#
# One of the primary distinctions between crowsetta and soundevent lies in
# their handling of labels/tags. While crowsetta employs a single textual label
# for each annotation, soundevent utilizes a list of key-value tags. This
# difference complicates the conversion process.

# %%
# By default, when converting to crowsetta format, the label field of the
# crowsetta annotation gets converted to a single tag with the key `crowsetta`
# and the value of the label field. However, numerous customization options are
# available to tailor this behavior. Refer to the
# [documentation][soundevent.io.crowsetta.label_to_tags] for more information.

label = "bird"
tags = cr.label_to_tags(label)
print(tags)

# %%
# In the reverse direction, the default behavior amalgamates all tags into a
# single label. For example:

tags = [
    Tag(key="species", value="bird"),
    Tag(key="color", value="red"),
]
label = cr.label_from_tags(tags)
print(label)

# %%
# Once again, you have the option to customize this behavior. Refer to the
# [documentation][soundevent.io.crowsetta.label_from_tags] for more information.
