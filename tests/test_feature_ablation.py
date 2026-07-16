from scripts.feature_ablation import FEATURE_SETS
from scripts.tune_hgb import FEATURES, TARGET


def test_feature_sets_are_incrementally_nested() -> None:
    sets = list(FEATURE_SETS.values())
    assert all(
        set(smaller).issubset(larger) for smaller, larger in zip(sets, sets[1:], strict=False)
    )
    assert sets[-1] == FEATURES


def test_feature_ablation_excludes_target_metadata() -> None:
    for features in FEATURE_SETS.values():
        assert TARGET not in features
        assert "target_uncertain" not in features
