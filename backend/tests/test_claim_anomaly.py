import numpy as np

from app.ml.claim_anomaly import feature_deviation_context, fit_anomaly_model


def test_fit_anomaly_model_is_reproducible() -> None:
    matrix = np.asarray(
        [
            [1.0, 10.0],
            [1.1, 10.5],
            [0.9, 9.8],
            [1.2, 10.2],
            [8.0, 90.0],
        ]
    )

    first = fit_anomaly_model(matrix, contamination=0.2, random_state=42)
    second = fit_anomaly_model(matrix, contamination=0.2, random_state=42)

    np.testing.assert_allclose(first.scores, second.scores)
    assert first.threshold == second.threshold


def test_feature_deviation_context_is_descriptive() -> None:
    row = np.asarray([10.0] * 11)
    medians = np.asarray([1.0] * 11)
    mads = np.asarray([1.0] * 11)

    context = feature_deviation_context(row, medians, mads, limit=2)

    assert context["type"] == "feature_deviation_context"
    assert len(context["top_deviations"]) == 2
    assert "causal" in context["note"].lower()
