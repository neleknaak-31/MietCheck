import numpy as np

from scripts.train_final_model import (
    FEATURES,
    TARGET,
    finite_sample_quantile,
    interval_metrics,
)


def test_finite_sample_quantile_is_conservative() -> None:
    residuals = np.arange(1, 101, dtype="float64")
    assert finite_sample_quantile(residuals, alpha=0.1) == 91.0


def test_interval_metrics_reports_expected_coverage() -> None:
    y_true = np.array([1.0, 2.0, 3.0])
    prediction = np.array([1.0, 2.5, 5.0])
    result = interval_metrics(y_true, prediction, 1.0)
    assert result["coverage"] == 2 / 3
    assert result["mean_width_eur_sqm"] == 2.0


def test_final_features_exclude_target_metadata() -> None:
    assert TARGET not in FEATURES
    assert "target_uncertain" not in FEATURES
