"""
# Saving and Loading data

In `soundevent`, we use the **Acoustic Objects Exchange Format** (**AOEF**) for
storing and exchanging audio objects. **AOEF** is a JSON-based format
specifically designed to standardize the representation of bioacoustic data,
enabling effective sharing and collaboration among researchers.

To demonstrate how to save and load data in **AOEF** format, we provide
examples below:

"""

# %%
# ## Loading Datasets
# Suppose we have an example dataset stored in the **AOEF** format. The dataset
# is stored as a text file following the JSON structure. To view the contents
# of the file, you can use the following code.

import json
from pathlib import Path

dataset_path = Path("example_dataset.json")
with open(dataset_path) as file:
    dataset_contents = json.load(file)

print(json.dumps(dataset_contents, indent=4))

# %%
# However, using the loading functions provided by the `soundevent` package,
# you can directly load the data into Python and obtain a `Dataset` object
# defined in the `soundevent.data` module:

from soundevent import io

dataset = io.load_dataset(dataset_path)
print(repr(dataset))

# %%
# By using the `load_dataset` function, you can access and analyze the dataset
# with all its recordings and related objects structured in a standardized and
# manageable way.

recording = dataset.recordings[0]
print(f"First recording: {recording!r}")
print(f"Recording tags: {recording.tags}")

# %%
# If you have your own dataset, you can save it to a file using the following
# code:

io.save_dataset(dataset, "my_dataset.json")
