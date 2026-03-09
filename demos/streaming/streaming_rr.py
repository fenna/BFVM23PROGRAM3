from collections import deque
import numpy as np
from wfdb import processing
from contextlib import contextmanager
import os, sys

# Quiet‑mode for WFDB: suppresses "Learning..." messages from X‑QRS.
os.environ["WFDB_QUIET"] = "1"
@contextmanager
def suppress_stdout():
    saved_stdout = sys.stdout
    devnull = open(os.devnull, 'w')
    sys.stdout = devnull
    try:
        yield
    finally:
        sys.stdout = saved_stdout
        devnull.close()


class StreamingRR_XQRS:
    """
    Online R-peak detector that uses WFDB's X-QRS algorithm on a sliding window.

    The detector emulates a real-time ECG acquisition pipeline:

    1. A fixed-length circular buffer (`deque`) stores the most recent
       ``window_sec`` seconds of raw ECG samples.
    2. After each new sample is added, the buffer is fed to
       ``wfdb.processing.xqrs_detect`` (with learning disabled) to obtain
       the indices of any QRS complexes that lie inside the window.
    3. Detected peaks are converted to absolute timestamps, filtered by a
       physiological refractory period, and stored in ``peak_times``.
    4. Consecutive timestamps are used to compute RR intervals, which are
       accessible via :meth:`latest_rr`.

    This class is deliberately lightweight -it does **no filtering** of the
    input signal (the caller may apply a bandpass filter beforehand) and it
    only returns the timestamps and RR intervals needed for downstream
    analysis (e.g., changepoint detection, heartrate variability).

    Parameters
    ----------
    fs : int or float
        Sampling frequency of the incoming ECG signal (samples per second).
    window_sec : float, optional (default=5.0)
        Length of the sliding window in seconds.  The window must be long
        enough to contain several heartbeats (typically ≥2s) so that the
        X-QRS algorithm can estimate its adaptive thresholds.
    refractory_ms : int, optional (default=250)
        Minimum allowed interval between two detected R-peaks, expressed in
        milliseconds.  This implements a physiological refractory period
        (≈250ms for a healthy adult) and prevents the same QRS complex
        from being reported multiple times as the window slides forward.

    Attributes
    ----------
    fs : float
        Sampling frequency (copied from the constructor argument).
    window_len : int
        Number of samples that constitute the sliding window
        (``window_sec * fs`` rounded down to an integer).
    buffer : collections.deque
        Circular buffer that holds the most recent ``window_len`` raw ECG
        samples.  Its ``maxlen`` ensures old samples are automatically
        discarded.
    refractory : int
        Refractory period expressed in samples (``refractory_ms * fs / 1000``).
    abs_index : int
        Absolute sample index of the **next** sample to be added.  It starts
        at ``0`` and increments after each call to :meth:`add`.
    last_peak_abs : int
        Absolute index of the most recent confirmed R-peak.  Initialized to
        ``-np.inf`` so that the first detected peak is always accepted.
    peak_times : list[float]
        List of timestamps (in seconds) of all confirmed R-peaks.
    rr_intervals : list[float]
        List of RR intervals (in seconds) computed from consecutive entries
        in ``peak_times``.

    Notes
    -----
    * The X-QRS detector is invoked inside a ``suppress_stdout`` context
      manager to silence the informational messages it prints to STDOUT
      (e.g., “Running QRS detection…”).  This does not affect the
      detection logic.
    * The class does **not** perform any additional preprocessing
      (baseline wander removal, notch filtering, etc.).  If the raw ECG
      contains substantial noise, apply a band-pass filter before feeding it
      to :meth:`add`.
    * The detector assumes a single-lead ECG where the QRS complex is the
      dominant feature.  Multi-lead signals should be reduced to a single
      lead (e.g., LeadII) before use.

    Example
    -------
    >>> import wfdb, numpy as np
    >>> from collections import deque
    >>> # Load a record (LeadII)
    >>> rec = wfdb.rdrecord('100', pn_dir='mitdb')
    >>> fs = rec.fs
    >>> raw_ecg = rec.p_signal[:, 0]
    >>> # Initialise the streaming detector
    >>> rr_detector = StreamingRR_XQRS(fs, window_sec=5.0, refractory_ms=250)
    >>> # Simulate streaming by feeding one sample at a time
    >>> for sample in raw_ecg:
    ...     rr_detector.add(sample)
    ...     if rr_detector.latest_rr() is not None:
    ...         print(f"RR = {rr_detector.latest_rr():.3f}s")
    """

    def __init__(self, fs, window_sec=5.0, refractory_ms=250):
        """
        Initialise the streaming detector.

        Parameters
        ----------
        fs : int or float
            Sampling frequency of the ECG signal (samples per second).
        window_sec : float, optional
            Length of the sliding window in seconds (default = 5 s).
        refractory_ms : int, optional
            Minimum interval between two accepted peaks in milliseconds
            (default = 250 ms).
        """
        self.fs = fs
        self.window_len = int(window_sec * fs)
        #######
        # This is the core of the streaming behaviour: 
        # you continuously push new ECG samples into self.buffer; 
        # the deque silently drops the oldest sample, 
        # so the buffer always represents the most 
        # recent window_sec seconds of data. 
        # No explicit “pop‑oldest” code is needed, 
        # and the memory usage stays bounded (O(window_len)
        self.buffer = deque(maxlen=self.window_len)
        #########
        self.refractory = int(refractory_ms * fs / 1000)
        self.abs_index = 0
        self.last_peak_abs = -np.inf
        self.peak_times = []
        self.rr_intervals = []

    def add(self, value):
        """
        Add a new ECG sample and update the internal R-peak detection state.

        The method performs the following steps:

        1. Append the new sample to the sliding buffer.
        2. Increment ``abs_index`` (the absolute sample counter).
        3. If the buffer is not yet full, exit early – detection requires a
           full window.
        4. Run ``wfdb.processing.xqrs_detect`` on the buffered segment
           (learning disabled) to obtain relative peak indices.
        5. Convert those relative indices to absolute sample numbers.
        6. For each absolute peak index:
           * Discard it if it occurs within the refractory period.
           * Otherwise record the timestamp (seconds) in ``peak_times``.
           * If a previous peak exists, compute the RR interval and store
             it in ``rr_intervals``.

        Parameters
        ----------
        value : float
            The next raw ECG sample (voltage) to be processed.
        """
        self.buffer.append(value)
        self.abs_index += 1

        # Wait until the buffer contains a full window before detecting.
        if len(self.buffer) < self.window_len:
            return

        # Run X‑QRS on the current window while silencing its stdout output.
        with suppress_stdout():
            peaks_rel = processing.xqrs_detect(
                np.array(self.buffer), self.fs, learn=False
            )

        # Convert relative indices (0 … window_len‑1) to absolute indices.
        oldest_abs = self.abs_index - self.window_len + 1
        peaks_abs = oldest_abs + peaks_rel

        # Process each detected peak.
        for p_abs in peaks_abs:
            # Enforce the physiological refractory period.
            if p_abs - self.last_peak_abs < self.refractory:
                continue

            if p_abs > self.last_peak_abs:
                # Accept the new peak.
                self.last_peak_abs = p_abs
                t = p_abs / self.fs
                self.peak_times.append(t)

                # Compute RR interval if we have at least two peaks.
                if len(self.peak_times) >= 2:
                    self.rr_intervals.append(
                        self.peak_times[-1] - self.peak_times[-2]
                    )

    def latest_rr(self):
        """
        Return the most recent RR interval (in seconds).

        Returns
        -------
        float or None
            The last computed RR interval if at least two peaks have been
            detected; otherwise ``None``.

        Notes
        -----
        The method does **not** compute a new RR interval – it merely returns
        the last value stored in ``self.rr_intervals``.  Call this after each
        ``add`` invocation to obtain a real‑time heart‑rate estimate:

        >>> rr = detector.latest_rr()
        >>> if rr is not None:
        >>>     hr = 60.0 / rr   # beats per minute
        """
        return self.rr_intervals[-1] if self.rr_intervals else None
    