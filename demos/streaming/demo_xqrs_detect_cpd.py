import numpy as np
import wfdb 
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import butter, filtfilt

from river import drift
from streaming_rr import StreamingRR_XQRS
from helper_functions import insert_pvc
from plot_functions import setup_ecg_plot   
from cusum import CusumDetector


#  Load a clean record and inject a PVC burst
record = wfdb.rdrecord('100', pn_dir='mitdb')
fs = record.fs
raw_sig = record.p_signal[:, 0]        # Lead II

# Insert three PVCs at 10 s, 11 s, 12 s
sig = insert_pvc(raw_sig, fs, pvc_time_sec=10.0)
sig = insert_pvc(sig,      fs, pvc_time_sec=11.0)
sig = insert_pvc(sig,      fs, pvc_time_sec=12.0)


# Instantiate RR‑peak detector and change‑point detector
rr_processor = StreamingRR_XQRS(fs=fs,
                               window_sec=5.0,
                               refractory_ms=100)   

cp_detector = drift.PageHinkley(threshold=12.5, delta=0.005) 
  


# Plot setup
fig, ax, ecg_line, peak_scatter, cp_vline = setup_ecg_plot(sig)

# Animation parameters (20 ms per frame → ~50 fps)
CHUNK_DURATION_SEC = 0.002
CHUNK_SIZE = int(fs * CHUNK_DURATION_SEC)
TOTAL_CHUNKS = len(sig) // CHUNK_SIZE


# Animation update function
global_idx = 0
delay_correction = CHUNK_DURATION_SEC / 2.0
ALIGN_TO_PEAK = True

def animate(frame):
    global global_idx

    start = frame * CHUNK_SIZE
    end   = start + CHUNK_SIZE
    chunk = sig[start:end]

    if len(chunk) == 0:
        anim.event_source.stop()
        return ecg_line, peak_scatter, cp_vline

    for sample in chunk:
        rr_processor.add(sample)
    global_idx += len(chunk)

    # Update ECG trace
    times = np.arange(global_idx) / fs
    mask = times >= times[-1] - 10
    ecg_line.set_data(times[mask], sig[:global_idx][mask])

    ###########################################################
    # here are the peak times detected by the streaming X‑QRS algorithm 
    # (stored in rr_processor.peak_times)
    # which are corrected by subtracting half the chunk duration 
    # to align with the true peaks in the ECG trace.
    visible_peaks = np.array(rr_processor.peak_times) - delay_correction
    ###########################################################

    # update the green‑dot scatter plot (peak_scatter) 
    # so that only the R‑peaks that belong to the currently visible 10‑second 
    # window are shown, and their y‑values are taken from the original ECG signal
    pmask = (visible_peaks >= times[-1] - 10) & (visible_peaks <= times[-1])
    peak_vals = np.interp(visible_peaks[pmask],
                          np.arange(global_idx) / fs,
                          sig[:global_idx])
    peak_scatter.set_offsets(np.c_[visible_peaks[pmask], peak_vals])

    # get the latest RR interval from the streaming processor and 
    # feed it to the change‑point detector
    latest_rr = rr_processor.latest_rr()
    if latest_rr is not None:
        print(f"[{times[-1]:.2f}s] RR = {latest_rr:.3f}s  (HR ≈ {60.0/latest_rr:.1f} bpm)")
        
        ##############################
        # Here the change‑point detector is updated with 
        # the latest RR interval, and if a change is detected, 
        # a vertical line is plotted at the corresponding timestamp.

        cp_detector.update(latest_rr)  
        if cp_detector.drift_detected:
            print("CHANGE DETECTED!")
            if ALIGN_TO_PEAK:
                # Align to the *corrected* peak timestamp (same as green dots)
                cp_time = rr_processor.peak_times[-1] - delay_correction
            else:
                # Align to the current right‑most time of the window
                cp_time = times[-1]
            cp_vline.set_xdata([cp_time, cp_time])   # a sequence of two identical values
            cp_vline.set_visible(True)
        ##############################

    ax.set_xlim(times[-1] - 10, times[-1])
    return ecg_line, peak_scatter, cp_vline


# Run the animation
anim = FuncAnimation(fig,
                    animate,
                    frames=TOTAL_CHUNKS,
                    interval=int(CHUNK_DURATION_SEC * 1000),
                    blit=True,
                    repeat=False)

plt.show()