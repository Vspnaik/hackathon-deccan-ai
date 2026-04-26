"""
Score calibration utilities.
Provides sigmoid (Platt) scaling for small datasets.
Isotonic regression stub for when enough labelled data exists.
"""
import math


def sigmoid_calibrate(score: float, scale: float = 2.5, shift: float = 0.0) -> float:
    """
    Platt/sigmoid calibration: maps raw score to [0, 1] probability.
    
    Args:
        score: Raw score value.
        scale: Controls steepness of sigmoid curve.
        shift: Horizontal shift of the sigmoid center.
    
    Returns:
        Calibrated probability in [0, 1].
    """
    try:
        return 1.0 / (1.0 + math.exp(-scale * (score - shift)))
    except OverflowError:
        return 0.0 if score < shift else 1.0


def linear_calibrate(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Simple linear rescaling to [0, 1]."""
    if max_val == min_val:
        return 0.5
    return max(0.0, min(1.0, (score - min_val) / (max_val - min_val)))


def isotonic_calibrate(scores: list, labels: list):
    """
    Isotonic regression calibration for when >= 300 labelled pairs exist.
    Returns a fitted calibrator function.
    
    Usage:
        calibrator = isotonic_calibrate(train_scores, train_labels)
        calibrated = calibrator(new_score)
    """
    try:
        from sklearn.isotonic import IsotonicRegression
        ir = IsotonicRegression(out_of_bounds="clip")
        ir.fit(scores, labels)
        return lambda x: float(ir.predict([x])[0])
    except ImportError:
        print("[Calibration] scikit-learn not available. Using sigmoid fallback.")
        return lambda x: sigmoid_calibrate(x)
