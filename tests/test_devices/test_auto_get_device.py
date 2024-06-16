import pytest

import pygmc

parametrize_data = [
    (x["version_example"], x["device_class"])
    for x in pygmc.devices.auto_get_device.device_match_list
    if x["version_example"]
]


@pytest.mark.parametrize("version_example,device_class", parametrize_data)
def test_matching_device_version_to_class(version_example, device_class):
    result_device_class = pygmc.devices.auto_get_device._get_matched_class_from_version(
        version_example
    )
    assert result_device_class == device_class


def test_bad_matching_device():
    # Welp... ambiguous version specs causes these bad matches
    # bugs become features... so add this test to raise attention if regex changes
    version_example = "GMC-6000"
    result_device_class = pygmc.devices.auto_get_device._get_matched_class_from_version(
        version_example
    )
    assert result_device_class == pygmc.devices.GMC600


def test_non_matching_device():
    # May change this to raise exception instead of returning None
    version_example = "GMC-420"
    result_device_class = pygmc.devices.auto_get_device._get_matched_class_from_version(
        version_example
    )
    assert result_device_class is None
