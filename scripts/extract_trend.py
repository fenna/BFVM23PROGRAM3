""" module to extract trend from time series data"""

__author__ ="Fenna Feenstra"
__version__ = "1.0"
__email__ = "f.feenstra@pl.hanze.nl"
__status__ = "Development"
__date__ = "2025-05-06"

import numpy as np
import pandas as pd


class TrendExtractor:
    """
    A class to extract smoothed trends from a time series using various filtering techniques.

    Parameters
    ----------
    series : pd.Series
        A time series (indexed by Period or datetime) to apply trend extraction methods on.
    """

    def __init__(self, series: pd.Series):
        self.series = series
        self.trend = None

    def rolling(self, window: int = 3, center: bool = True) -> pd.Series:
        """
        Apply a simple moving average to smooth the series.

        Parameters
        ----------
        window : int
            Number of periods in the moving average window.
        center : bool
            Whether to center the moving average window.

        Returns
        -------
        pd.Series
            The smoothed trend.
        """
        trend = self.series.rolling(window=window, center=center).mean()
        self.trend = trend
        return trend

    def lowess(self, frac: float = 0.1) -> pd.Series:
        """
        Apply LOWESS (Locally Weighted Scatterplot Smoothing).

        Parameters
        ----------
        frac : float
            The fraction of the data used when estimating each y-value.

        Returns
        -------
        pd.Series
            The smoothed trend.
        """
        from statsmodels.nonparametric.smoothers_lowess import lowess
        smoothed = lowess(self.series.values,
                          self.series.index.to_timestamp().astype(np.int64),
                          frac=frac,
                          return_sorted=False)
        trend = pd.Series(smoothed, index=self.series.index)
        self.trend = trend
        return trend

    def kalman(self, n_iter: int = 5, n_dim_obs: int = 1) -> pd.Series:
        """
        Apply a Kalman filter to estimate the smoothed trend.

        Parameters
        ----------
        n_iter : int
            Number of iterations for Expectation-Maximization optimization.
        n_dim_obs : int
            Number of observed dimensions (usually 1 for a univariate series).

        Returns
        -------
        pd.Series
            The smoothed trend.
        """
        from pykalman import KalmanFilter
        values = self.series.values
        kf = KalmanFilter(initial_state_mean=values[0], n_dim_obs=n_dim_obs)
        kf = kf.em(values, n_iter=n_iter)
        state_means, _ = kf.filter(values)
        trend = pd.Series(state_means.flatten(), index=self.series.index)
        self.trend = trend
        return trend

    def savgol(self, window: int = 12, polyorder: int = 2) -> pd.Series:
        """
        Apply Savitzky-Golay filter for polynomial smoothing.

        Parameters
        ----------
        window : int
            Length of the filter window (must be odd and > polyorder).
        polyorder : int
            Order of the polynomial used to fit the samples.

        Returns
        -------
        pd.Series
            The smoothed trend.
        """
        from scipy.signal import savgol_filter
        #for each window it uses closest points
        smoothed = savgol_filter(self.series, window_length=window, polyorder=polyorder)
        trend = pd.Series(smoothed, index=self.series.index)
        self.trend = trend
        return trend

    def lowpass(self, cutoff: float = 0.1, fs: float = 1.0, order: int = 4) -> pd.Series:
        """
        Apply a Butterworth low-pass filter.

        Parameters
        ----------
        cutoff : float
            Cutoff frequency of the filter (in Hz).
        fs : float
            Sampling frequency of the series.
        order : int
            Order of the filter.

        Returns
        -------
        pd.Series
            The smoothed trend.
        """
        from scipy.signal import butter, filtfilt
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        smoothed = filtfilt(b, a, self.series)
        trend = pd.Series(smoothed, index=self.series.index)
        self.trend = trend
        return trend

    def fourier(self, keep: int = 10) -> pd.Series:
        """
        Apply a Fourier transform and keep only low-frequency components.

        Parameters
        ----------
        keep : int
            Number of low-frequency components to keep in the FFT spectrum.

        Returns
        -------
        pd.Series
            The smoothed trend reconstructed from filtered FFT.
        """
        fft = np.fft.fft(self.series)
        fft_filtered = np.copy(fft)
        fft_filtered[keep:-keep] = 0
        smoothed = np.fft.ifft(fft_filtered).real
        trend = pd.Series(smoothed, index=self.series.index)
        self.trend = trend
        return trend

def original(self) -> pd.Series:        
        """
        Return the original series without any smoothing.

        Returns
        -------
        pd.Series
            The original series.
        """
        self.trend = self.series
        return self.series

    

if __name__ == "__main__":
    # Example usage
    data = {
        'date': pd.date_range(start='2020-01-01', periods=100, freq='M'),
        'value': np.random.randn(100).cumsum()
    }
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    series = df['value']
    extractor = TrendExtractor(series)
    smoothed_series = extractor.rolling(window=5)
    print(smoothed_series)

