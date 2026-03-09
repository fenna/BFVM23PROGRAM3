import math
from typing import Optional

class CusumDetector:
    """
    Classic one‑sided CUSUM change‑point detector for a scalar stream
    (e.g., RR intervals).  API compatible with River's drift detectors:
        det = CusumDetector(delta=0.5, threshold=5.0)
        det.update(value)
        if det.drift_detected:   # True ⇢ change detected
            ...
    """

    def __init__(
        self,
        *,
        delta: float = 0.5,          # slack factor (k = delta * sigma)
        threshold: float = 5.0,      # detection threshold (h = threshold * sigma)
        min_samples: int = 30        # wait until we have a reliable sigma estimate
    ):
        self.delta = delta
        self.threshold_factor = threshold
        self.min_samples = min_samples

        # Running statistics (Welford's algorithm)
        self.n = 0
        self.mean: Optional[float] = None
        self.M2: Optional[float] = None   # sum of squares of differences

        # CUSUM state
        self.s_pos = 0.0
        self.s_neg = 0.0
        self.k = 0.0          # slack term (computed after enough samples)
        self.h = 0.0          # detection threshold (computed after enough samples)

        self.drift_detected = False

    # ------------------------------------------------------------------
    # Incremental mean / variance (Welford)
    # ------------------------------------------------------------------
    def _update_mean_variance(self, x: float) -> None:
        if self.n == 0:
            self.mean = x
            self.M2 = 0.0
        else:
            delta = x - self.mean
            self.mean += delta / (self.n + 1)
            self.M2 += delta * (x - self.mean)   # uses the new mean
        self.n += 1

    # ------------------------------------------------------------------
    # Public update method – call once per new RR interval
    # ------------------------------------------------------------------
    def update(self, x: float) -> None:
        self._update_mean_variance(x)

        # Need a minimum number of samples to get a stable sigma
        if self.n < self.min_samples:
            self.drift_detected = False
            return

        # Standard deviation (add a tiny epsilon to avoid divide‑by‑zero)
        sigma = math.sqrt(self.M2 / (self.n - 1) + 1e-12)

        # Initialise slack (k) and threshold (h) the first time we have sigma
        if self.k == 0.0:
            self.k = self.delta * sigma
            self.h = self.threshold_factor * sigma

        # Positive CUSUM (detect upward shift)
        self.s_pos = max(0.0, self.s_pos + (x - self.mean - self.k))

        # Negative CUSUM (detect downward shift)
        self.s_neg = max(0.0, self.s_neg + (self.mean - x - self.k))

        # Check for a change
        if self.s_pos > self.h or self.s_neg > self.h:
            self.drift_detected = True
            # Reset so we can detect a *new* change later
            self.s_pos = 0.0
            self.s_neg = 0.0
            # Optional: re‑initialise the reference statistics with the current point
            self.mean = x
            self.M2 = 0.0
            self.n = 1
        else:
            self.drift_detected = False