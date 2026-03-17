from flask import Flask, jsonify
import threading
import time
import numpy as np

app = Flask(__name__)

data = []

def signal_generator():
    t = 0
    while True:
        value = np.sin(0.2 * t) + np.random.normal(0, 0.2)
        data.append(float(value))

        if len(data) > 1_000:   # prevent unbounded growth
            data.pop(0)

        t += 1
        time.sleep(1)

@app.route("/data")
def get_data():
    return jsonify(data)

thread = threading.Thread(target=signal_generator)
thread.daemon = True
thread.start()

app.run(host="0.0.0.0", port=5000)