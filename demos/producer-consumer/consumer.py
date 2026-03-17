import requests
import time
import numpy as np

WINDOW = 20   # set to None for full history

history = []

while True:
    r = requests.get("http://localhost:5000/data")
    data = r.json()

    if WINDOW:
        values = data[-WINDOW:]
    else:
        values = data

    if values:
        avg = np.mean(values)
        mx = np.max(values)

        print(f"n={len(values)}   mean={avg:.3f}   max={mx:.3f}")

    time.sleep(1)