import pandas as pd

from scripts.tune_hgb import (
    FEATURES,
    PARAMETER_CANDIDATES,
    TARGET,
    spatial_group_partition,
    validate_partitions,
)


def test_spatial_group_partition_is_disjoint_and_deterministic() -> None:
    groups = pd.Series([f"group_{index}" for index in range(100)])
    first = spatial_group_partition(groups)
    second = spatial_group_partition(groups)

    validate_partitions(first)
    assert first == second
    assert set().union(*first.values()) == set(groups)
    assert {name: len(values) for name, values in first.items()} == {
        "calibration": 15,
        "test": 15,
        "development": 70,
    }


def test_tuning_excludes_target_and_has_bounded_search_space() -> None:
    assert TARGET not in FEATURES
    assert "target_uncertain" not in FEATURES
    assert len(PARAMETER_CANDIDATES) == 8
    assert all(candidate["max_iter"] <= 350 for candidate in PARAMETER_CANDIDATES)
