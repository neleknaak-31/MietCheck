from scripts.pilot_model import CONTEXT_FEATURES, TARGET


def test_target_and_target_metadata_are_not_model_features() -> None:
    assert TARGET not in CONTEXT_FEATURES
    assert "target_uncertain" not in CONTEXT_FEATURES

