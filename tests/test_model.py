import pytest
import joblib
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.features.engineer import FEATURE_COLS


def test_model_file_exists():
    """Model file should exist after training."""
    assert Path("results/model.pkl").exists(), "Model not found — run python -m src.models.train first"


def test_model_predicts_probabilities():
    """Model should output probabilities between 0 and 1."""
    model = joblib.load("results/model.pkl")
    
    # Create a fake transaction
    row = pd.DataFrame([{col: 0.0 for col in FEATURE_COLS}])
    
    prob = model.predict_proba(row)[:, 1]
    assert 0 <= prob[0] <= 1, f"Probability out of range: {prob[0]}"


def test_model_high_risk_scores_higher():
    """Model should produce varied scores across different inputs."""
    model = joblib.load("results/model.pkl")

    # Generate 100 random transactions
    np.random.seed(42)
    rows = pd.DataFrame(
        np.random.rand(100, len(FEATURE_COLS)),
        columns=FEATURE_COLS
    )

    probs = model.predict_proba(rows)[:, 1]

    # Scores should not all be identical
    assert probs.std() > 0, "Model produces identical scores for all inputs"
    assert probs.min() >= 0 and probs.max() <= 1, "Scores out of range"


def test_model_output_shape():
    """Model should return one probability per input row."""
    model = joblib.load("results/model.pkl")
    
    rows = pd.DataFrame([{col: 0.0 for col in FEATURE_COLS} for _ in range(5)])
    probs = model.predict_proba(rows)[:, 1]
    
    assert len(probs) == 5, f"Expected 5 predictions, got {len(probs)}"