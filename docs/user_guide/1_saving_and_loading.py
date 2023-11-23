"""
# Saving and Loading data

In `soundevent`, we use the **Acoustic Objects Exchange Format** (**AOEF**) for
storing and exchanging audio objects. **AOEF** is a JSON-based format
specifically designed to standardize the representation of computational
bioacoustic data, enabling effective sharing and collaboration among
researchers.

!!! note "Why JSON?"

    [JSON](https://www.json.org/) or JavaScript Object Notation, is a
    lightweight data-interchange format that is widely supported across various
    platforms and programming languages. It provides human-readable syntax and
    is commonly used in web applications, making it an ideal choice for data
    exchange.

To demonstrate how to save and load data in **AOEF** format, we provide
examples below:

"""


# %%
# ## Datasets
# Suppose we have an example dataset stored in the **AOEF** format. The dataset
# is stored as a text file following the [JSON](https://www.json.org/)
# structure. To view the contents of the file, you can use the following code.

import json
from pathlib import Path

dataset_path = Path("example_dataset.json")
with open(dataset_path) as file:
    dataset_contents = json.load(file)

print(json.dumps(dataset_contents, indent=2))

# %%
# ### Loading Datasets
# By using the loading functions provided by the `soundevent` package, you can
# directly load the data into Python and obtain a
# [`Dataset`](../../data.md#datasets) object.

from soundevent import io

dataset = io.load(dataset_path)
print(repr(dataset))

# %%
# The [`load_dataset`][soundevent.io.load_dataset] function allows you to
# access and analyze the dataset, which contains recordings and related
# objects, all structured in a standardized and manageable way.

recording = dataset.recordings[0]
print(f"First recording: {recording!r}")
print(f"Recording tags: {recording.tags}")

# %%
# ### Saving Datasets
# If you have your own dataset, you can save it to a file using the
# [`save_dataset`][soundevent.io.save_dataset] function. This function stores
# the dataset in **AOEF** format, ensuring compatibility and easy sharing with
# other researchers.

io.save(dataset, dataset_path)

# %%
# ## Annotation Projects
#
# Similar to loading datasets, you can use the
# [`load_annotation_project`][soundevent.io.load_annotation_project] function
# to load annotations stored in the **AOEF** format.
#
# Here we have transformed 10 random annotated recordings from the
# [NIPS4BPlus](https://doi.org/10.7717%2Fpeerj-cs.223) dataset into the
# **AOEF** format and stored it in the `nips4b_plus_aoef.json` file. You can
# use the provided code to view the annotations.

annotation_path = Path("nips4b_plus_sample.json")
with open(annotation_path) as file:
    annotation_contents = json.load(file)

print(json.dumps(annotation_contents, indent=2))

# %%
# ### Loading Annotation Projects
# The [`load_annotation_project`][soundevent.io.load_annotation_project]
# function can be used to load the annotations into Python and obtain an
# [`AnnotationProject`](../../data.md#annotation_projects) object directly.

nips4b_sample = io.load(annotation_path, type="annotation_set")
print(repr(nips4b_sample))

# %%
# This object allows you to access and analyze the annotations, along with
# their associated objects.

for task in nips4b_sample.clip_annotations:
    clip = task.clip
    recording = clip.recording
    print(
        f"* Recording {recording.path} [from "
        f"{clip.start_time:.3f}s to {clip.end_time:.3f}s]"
    )
    print(f"\t{len(task.annotations)} annotations found")
    for annotation in task.annotations:
        sound_event = annotation.sound_event
        start_time, end_time = sound_event.geometry.coordinates
        print(f"\t+ Sound event from {start_time:.3f}s to {end_time:.3f}s")
        for tag in annotation.tags:
            print(f"\t\t- {tag}")
    print("")

# %%
# ### Saving Annotation Projects
# Saving the annotation project is just as straightforward using the
# [`save_annotation_project`][soundevent.io.save_annotation_project] function:

io.save(nips4b_sample, "nips4b_plus_sample.json")

# %%
# ## Model Runs
# Finally, the outputs of a model run can also be stored in the **AOEF**
# format. You can save and load model runs using the
# [`save_model_run`][soundevent.io.save_model_run] and
# [`load_model_run`][soundevent.io.load_model_run] functions, respectively. The
# loading function reads the **AOEF** file and returns a
# [`ModelRun`](../../data.md#model_run) object that can be used for further
# analysis.
#
# By utilizing the saving and loading functions provided by soundevent, you can
# easily manage and exchange acoustic data objects in AOEF format, promoting
# collaboration and advancing your bioacoustic research endeavors.
