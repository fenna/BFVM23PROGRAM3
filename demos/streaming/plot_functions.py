import matplotlib.pyplot as plt
import numpy as np

def setup_ecg_plot(
    sig,
    *,
    figsize=(10, 4),
    title="Streaming ECG - X-QRS (5s window) -PageHinkley (δ=0.01)",
    xlabel="Time (s)",
    ylabel="Amplitude (mV)",
    xlim_seconds=10,
    y_margin_factor=0.2,
    peak_color="limegreen",
    peak_size=30,
    line_color="steelblue",
    line_width=1,
    cp_color="red",
    cp_width=2,
    cp_style="--",
    legend_loc="upper right",
):
    """
    Initialise the Matplotlib canvas for a live ECG stream.

    Parameters
    ----------
    sig : array_like
        The raw (or filtered) ECG signal that will be plotted.
        Its min/max values are used to set a sensible y-limit.
    figsize : tuple, optional
        Figure size in inches (default ``(10, 4)``).
    title : str, optional
        Axes title.
    xlabel, ylabel : str, optional
        Axis labels.
    xlim_seconds : float, optional
        Width of the scrolling window in seconds (default 10 s).
    y_margin_factor : float, optional
        Fraction of the signal range that is added as margin on top and bottom.
        ``0.2`` → 20% extra space above and below the min/max.
    peak_color, peak_size : str / int, optional
        Appearance of the R-peak scatter markers.
    line_color, line_width : str / int, optional
        Appearance of the ECG trace line.
    cp_color, cp_width, cp_style : str / int / str, optional
        Appearance of the changepoint vertical line.
    legend_loc : str, optional
        Location of the legend (passed directly to ``ax.legend``).

    Returns
    -------
    fig : matplotlib.figure.Figure
        The created figure object.
    ax : matplotlib.axes.Axes
        The axes on which everything is drawn.
    ecg_line : matplotlib.lines.Line2D
        The line object that will be updated with the scrolling ECG data.
    peak_scatter : matplotlib.collections.PathCollection
        The scatter object for R‑peak markers.
    cp_vline : matplotlib.lines.Line2D
        The vertical line that indicates a detected changepoint.
    """
    fig, ax = plt.subplots(figsize=figsize)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    # Horizontal window (rolling view)
    ax.set_xlim(0, xlim_seconds)

    # Vertical limits – add a margin on both sides
    sig_min, sig_max = float(np.min(sig)), float(np.max(sig))
    y_range = sig_max - sig_min
    ax.set_ylim(sig_min - y_range * y_margin_factor,
                sig_max + y_range * y_margin_factor)

    # 2.1  ECG trace (will be updated each frame)
    ecg_line, = ax.plot([], [], lw=line_width, color=line_color)

    # 2.2  R‑peak markers (green dots)
    peak_scatter = ax.scatter([], [], color=peak_color,
                              s=peak_size, label="R‑peak")

    # 2.3  Changepoint vertical line (initially hidden)
    cp_vline = ax.axvline(x=-1, color=cp_color,
                          lw=cp_width, ls=cp_style,
                          label="Change point")
    cp_vline.set_visible(False)   # hide until a change is detected

    ax.legend(loc=legend_loc)

    return fig, ax, ecg_line, peak_scatter, cp_vline