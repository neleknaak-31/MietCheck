from scripts.algorithm_benchmark import FEATURES, TARGET, model_factories


def test_algorithm_benchmark_has_expected_candidates() -> None:
    assert set(model_factories()) == {
        "ridge",
        "random_forest",
        "hist_gradient_boosting",
        "mlp",
    }


def test_algorithm_benchmark_excludes_target_metadata() -> None:
    assert TARGET not in FEATURES
    assert "target_uncertain" not in FEATURES
