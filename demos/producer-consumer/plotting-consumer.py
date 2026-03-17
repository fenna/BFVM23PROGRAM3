import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

URL = "http://localhost:5000/data"
WINDOW = 50   

fig, ax = plt.subplots()

line_signal, _ = ax.plot([], [], label="signal")
line_mean, _ = ax.plot([], [], linestyle="--", label="mean", c='green')
max_point = ax.scatter([], [], s=80, label="max", zorder=3, c=['red'])

ax.set_xlabel("sample")
ax.set_ylabel("value")
ax.legend(loc='lower left')


def update(frame):
    global max_point

    r = requests.get(URL)
    data = r.json()

    if WINDOW:
        data = data[-WINDOW:]

    if len(data) == 0:
        return

    y = np.array(data)
    x = np.arange(len(y))

    mean = np.mean(y)

    max_idx = np.argmax(y)
    max_val = y[max_idx]

    line_signal.set_data(x, y)
    line_mean.set_data(x, np.full(len(x), mean))

    max_point.set_offsets([[max_idx, max_val]])

    ax.set_xlim(0, len(x))
    ax.set_ylim(y.min() - 0.5, y.max() + 0.5)


ani = FuncAnimation(fig, update, interval=1_000)

plt.show()