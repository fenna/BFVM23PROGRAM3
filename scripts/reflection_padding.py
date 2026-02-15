import numpy as np
from scipy.signal import savgol_filter

def reflect_pad(signal, pad_len):
    """Return signal padded by mirroring the edges."""
    left  = signal[1:pad_len+1][::-1]   # skip the first element to avoid duplicate
    right = signal[-pad_len-1:-1][::-1] # skip the last element
    return np.concatenate([left, signal, right])

# Example data
t = np.linspace(0, 2*np.pi, 100)
y = np.sin(t) + 0.2*np.random.randn(100)   # noisy sine

# Pad symmetrically with 10 points on each side
y_padded = reflect_pad(y, pad_len=20)

# Apply Savitzky‑Golay on the padded array (window must be odd)
window = 21   # 10 points each side + centre
polyorder = 3
y_sg = savgol_filter(y_padded, window_length=window, polyorder=polyorder)
# Remove the padding to get the final result aligned with original indices
y_sg_trimmed = y_sg[20:-20]

y_not_padded = savgol_filter(y, window_length=window, polyorder=polyorder)

# Quick plot (requires matplotlib)
import matplotlib.pyplot as plt
plt.plot(t, y, label='Noisy')
plt.plot(t, y_not_padded, label='Savitzky‑Golay (no padding)')
plt.plot(t, y_sg_trimmed, label='Savitzky‑Golay (reflected padding)')
plt.legend(); plt.show()