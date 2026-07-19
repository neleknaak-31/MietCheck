from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR, LinearSVR

from scripts.svm_kernel_benchmark import model_factories


def test_svm_study_has_linear_and_kernel_variants_with_scaling() -> None:
    models = model_factories()
    assert set(models) == {"linear_svr", "rbf_svr"}
    assert isinstance(models["linear_svr"](), Pipeline)
    assert isinstance(models["rbf_svr"](), Pipeline)
    for factory in models.values():
        model = factory()
        assert isinstance(model["prepare"]["scale"], StandardScaler)
    assert isinstance(models["linear_svr"]()["model"], LinearSVR)
    assert isinstance(models["rbf_svr"]()["model"], SVR)
