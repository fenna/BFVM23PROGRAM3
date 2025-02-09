import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
import websocket

# WebSocket server URL
ws_url = "ws://localhost:8080"

# Initialize empty lists to store data
x_data = []
y_data = []
ts = []

# Function to handle received data
def on_message(ws, message):
    # print (message)
    # >>> s = '0 days 00:00:00.016000,-0.1,-0.115'
    # >>> s.split(',')
    # ['0 days 00:00:00.016000', '-0.1', '-0.115']
    # >>>
    # Assuming message contains two float values separated by a comma
    # x_val, y_val = map(float, message.split(','))
    data = message.split(',')
    print (data)
    try:
        ts_val = datetime.strptime(data[0].split()[2], '%H:%M:%S.%f')
        x_val = float(data[1])
        y_val = float(data[2])
    except:
        print (f'{message} could not be parsed')

    # print (f'ts_val: {ts_val}')
    # print (f'x_val: {x_val}')
    # print (f'y_val: {y_val}')
    
    # Append the received values to the data lists
    ts.append(ts_val)
    x_data.append(x_val)
    y_data.append(y_val)

    # Check whether there are 500 data point in the list
    if len(ts) > 500:
        ts.pop(0)
        x_data.pop(0)
        y_data.pop(0)
              

# Function to handle WebSocket open
def on_open(ws):
    print("Connected to WebSocket server")

# Function to handle WebSocket close
def on_close(ws):
    print("Connection to WebSocket server closed")

# Create WebSocket connection
def run_websocket():
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_open=on_open,
                                on_close=on_close)
    ws.run_forever()

# Start WebSocket connection in a separate thread
websocket_thread = threading.Thread(target=run_websocket)
websocket_thread.start()

# Function to update the plot
def update(frame):
    # Clear previous plot
    plt.cla()
    # Plot the data
    plt.plot(ts, y_data)
    plt.ylim(-0.3, 1)
    # Set plot title and labels
    plt.title('ECG Plot')
    plt.xlabel('Time (ms)')
    plt.ylabel('ECG (mV)')

# Create a Matplotlib figure and axis
fig, ax = plt.subplots()

# Create an animation
ani = FuncAnimation(fig, update, interval=100) # Update plot every 1000 milliseconds (1 second)

# Show the plot
plt.show()

