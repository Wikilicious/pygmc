import pytest

from pygmc import Discovery

# position: 0=<GETVER>, 1=model, 2=revision
version_to_model_rev_test_cases = [
    # Actual data
    ("GMC-800Re1.08", "GMC-800", "1.08"),
    ("GMC-600+Re 2.52", "GMC-600+", "2.52"),
    ("GMC-500+Re 2.22", "GMC-500+", "2.22"),
    ("GMC-320Re 4.26", "GMC-320", "4.26"),
    ("GMC-300SRe 1.14", "GMC-300S", "1.14"),
    ("GMC-SE Re 1.05", "GMC-SE", "1.05"),
    # Fake test cases below
    ("", "", ""),  # GRC - non-match returns empty model & revision
    ("GMC 404 Re1.23A", "GMC 404", "1.23A"),  # test space in model
    ("GMC-800Pi3.14", "", ""),  # test non-matching input
]


@pytest.mark.parametrize("ver,model,rev", version_to_model_rev_test_cases)
def test_model_revision_parser(ver, model, rev):
    result_model, result_rev = Discovery._get_model_rev_from_version(ver)
    assert result_model == model, f"Input {ver=} - {result_model=}|{model=}"
    assert result_rev == rev, f"Input {ver=} - {result_rev=}|{rev=}"
