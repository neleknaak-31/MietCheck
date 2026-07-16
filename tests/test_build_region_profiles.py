import pandas as pd

from scripts.build_region_profiles import transform_centres, validate_centres


def test_transform_centres_places_berlin_in_expected_laea_range() -> None:
    centres = pd.DataFrame([{"region": "Berlin", "latitude": 52.52, "longitude": 13.405}])
    transformed = transform_centres(centres)
    assert 4_500_000 < transformed.loc[0, "x_laea_m"] < 4_700_000
    assert 3_200_000 < transformed.loc[0, "y_laea_m"] < 3_400_000


def test_validate_centres_rejects_region_drift() -> None:
    centres = pd.DataFrame([{"region": "Berlin", "latitude": 52.52, "longitude": 13.405}])
    validate_centres(centres, {"Berlin"})
