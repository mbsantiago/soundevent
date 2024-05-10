"""Test Suite for the soundevent.io.crowsetta.labels module."""

import soundevent.io.crowsetta as crowsetta_io
from soundevent import data


def test_label_from_tag_without_kwargs():
    tag = data.Tag(key="animal", value="dog")
    label = crowsetta_io.label_from_tag(tag)
    assert label == "animal:dog"


def test_label_from_tag_with_only_value():
    tag = data.Tag(key="animal", value="dog")
    label = crowsetta_io.label_from_tag(tag, value_only=True)
    assert label == "dog"


def test_label_from_tag_with_label_mapping():
    tag = data.Tag(key="crowsetta", value="dog")
    label = crowsetta_io.label_from_tag(
        tag,
        label_mapping={data.Tag(key="crowsetta", value="dog"): "cat"},
    )
    assert label == "cat"


def test_label_from_tag_with_label_mapping_missing_label():
    tag = data.Tag(key="crowsetta", value="dog")
    label = crowsetta_io.label_from_tag(
        tag,
        label_mapping={data.Tag(key="crowsetta", value="cat"): "dog"},
    )
    assert label == "crowsetta:dog"


def test_label_from_tag_with_label_fn():
    tag = data.Tag(key="crowsetta", value="dog")
    label = crowsetta_io.label_from_tag(
        tag,
        label_fn=lambda _: "cat",
    )
    assert label == "cat"


def test_label_from_tag_with_label_fn_and_label_mapping():
    tag = data.Tag(key="crowsetta", value="dog")
    label = crowsetta_io.label_from_tag(
        tag,
        label_fn=lambda _: "cat",  # type: ignore
        label_mapping={data.Tag(key="crowsetta", value="dog"): "bird"},
    )
    assert label == "cat"


def test_label_to_tags_with_custom_fn():
    label = "crowsetta-dog"
    tag = crowsetta_io.label_to_tags(
        label,
        tag_fn=lambda _: data.Tag(key="crowsetta", value="dog"),
    )
    assert tag == [data.Tag(key="crowsetta", value="dog")]


def test_label_to_tags_with_custom_fn_list():
    label = "crowsetta-dog"
    tag = crowsetta_io.label_to_tags(
        label,
        tag_fn=lambda _: [data.Tag(key="crowsetta", value="dog")],
    )
    assert tag == [data.Tag(key="crowsetta", value="dog")]


def test_label_to_tags_with_failing_custom_fn():
    def failing_fn(label):
        if label == "dog":
            raise ValueError("dog is not a valid label")
        return data.Tag(key="animal", value=label)

    label = "dog"
    tag = crowsetta_io.label_to_tags(
        label,
        tag_fn=failing_fn,
    )
    assert tag == [data.Tag(key="crowsetta", value="dog")]


def test_label_to_tags_with_tag_mapping_single_tag():
    label = "crowsetta-dog"
    tag = crowsetta_io.label_to_tags(
        label,
        tag_mapping={"crowsetta-dog": data.Tag(key="crowsetta", value="dog")},
    )
    assert tag == [data.Tag(key="crowsetta", value="dog")]


def test_label_to_tags_with_tag_mapping_tag_list():
    label = "crowsetta-dog"
    tag = crowsetta_io.label_to_tags(
        label,
        tag_mapping={"crowsetta-dog": [data.Tag(key="animal", value="dog")]},
    )
    assert tag == [data.Tag(key="animal", value="dog")]


def test_label_to_tags_with_tag_mapping_missing_label():
    label = "dog"
    tag = crowsetta_io.label_to_tags(
        label,
        tag_mapping={"cat": data.Tag(key="animal", value="cat")},
    )
    assert tag == [data.Tag(key="crowsetta", value="dog")]


def test_label_to_tags_with_key_mapping():
    key_mapping = {"bat": "animal", "female": "sex"}
    tag = crowsetta_io.label_to_tags(
        "bat",
        key_mapping=key_mapping,
    )
    assert tag == [data.Tag(key="animal", value="bat")]

    tag = crowsetta_io.label_to_tags(
        "female",
        key_mapping=key_mapping,
    )
    assert tag == [data.Tag(key="sex", value="female")]

    tags = crowsetta_io.label_to_tags(
        "large",
        key_mapping=key_mapping,
    )

    assert tags == [data.Tag(key="crowsetta", value="large")]


def test_label_to_tags_with_key_mapping_fallback():
    key_mapping = {"bat": "animal"}
    tag = crowsetta_io.label_to_tags(
        "dog", key_mapping=key_mapping, fallback="pet"
    )
    assert tag == [data.Tag(key="pet", value="dog")]


def test_label_to_tags_with_empty_labels():
    tags = crowsetta_io.label_to_tags(
        "__empty__",
    )
    assert tags == []

    tags = crowsetta_io.label_to_tags(
        "NA",
        empty_labels=["NA"],
    )
    assert tags == []


def test_label_from_tags_with_custom_fn():
    tags = [data.Tag(key="animal", value="cat")]
    label = crowsetta_io.label_from_tags(
        tags,
        seq_label_fn=lambda _: "dog",
    )
    assert label == "dog"


def test_label_from_tags_empty_list():
    label = crowsetta_io.label_from_tags([])
    assert label == "__empty__"

    label = crowsetta_io.label_from_tags([], empty_label="NA")
    assert label == "NA"


def test_label_from_tags_select_by_key():
    tags = [
        data.Tag(key="animal", value="dog"),
        data.Tag(key="sex", value="male"),
    ]
    label = crowsetta_io.label_from_tags(
        tags,
        select_by_key="animal",
    )
    assert label == "dog"

    label = crowsetta_io.label_from_tags(
        tags,
        select_by_key="sex",
    )
    assert label == "male"


def test_label_from_tags_select_by_key_missing_key():
    tags = [
        data.Tag(key="animal", value="dog"),
    ]
    label = crowsetta_io.label_from_tags(
        tags,
        select_by_key="sex",
    )
    assert label == "__empty__"

    label = crowsetta_io.label_from_tags(
        tags,
        select_by_key="sex",
        empty_label="NA",
    )
    assert label == "NA"


def test_label_from_tags_select_by_index():
    tags = [
        data.Tag(key="animal", value="dog"),
        data.Tag(key="sex", value="male"),
    ]
    label = crowsetta_io.label_from_tags(
        tags,
        index=0,
        value_only=True,
    )
    assert label == "dog"

    label = crowsetta_io.label_from_tags(
        tags,
        index=1,
        value_only=False,
    )
    assert label == "sex:male"

    label = crowsetta_io.label_from_tags(
        tags,
        index=2,
        value_only=False,
    )
    assert label == "animal:dog"

    label = crowsetta_io.label_from_tags(
        tags,
        index=-1,
        value_only=True,
    )
    assert label == "male"


def test_label_from_tags_concat_all():
    tags = [
        data.Tag(key="animal", value="dog"),
        data.Tag(key="sex", value="male"),
    ]

    label = crowsetta_io.label_from_tags(
        tags,
    )
    assert label == "animal:dog,sex:male"


def test_label_from_tags_with_custom_separator():
    tags = [
        data.Tag(key="animal", value="dog"),
        data.Tag(key="sex", value="male"),
    ]

    label = crowsetta_io.label_from_tags(
        tags,
        separator="|",
    )
    assert label == "animal:dog|sex:male"
