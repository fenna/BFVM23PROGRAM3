import asyncio
import websockets
import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation

df = pd.DataFrame(columns=["time", "value"])
max_save = 100

async def receive_data():
    """Receive WebSocket data and update the DataFrame asynchronously."""
    global df
    async with websockets.connect("ws://localhost:8765") as websocket:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket closed")
                break

def animate(frame):
    """Update the Matplotlib plot with new data."""
    global df
    if not df.empty:
        df_to_plot = df.tail(max_save).reset_index(drop=True)

        ax.clear()
        ax.set_ylim(-1.5, 1.5)
        ax.set_xlabel("Time")
        ax.set_ylabel("Value")
        ax.set_xlim(df_to_plot["time"].min(), df_to_plot["time"].max() + 1)
        
        ax.plot(df_to_plot["time"], df_to_plot["value"], "b-", label="Sine Wave")
        ax.legend()

async def main():
    """Run the WebSocket listener and Matplotlib event loop together."""
    task = asyncio.create_task(receive_data())  
    ani = animation.FuncAnimation(fig, animate, interval=100, save_count=max_save)
    plt.show(block=False)

    while True:
        await asyncio.sleep(0.1)  # Keep async loop running for WebSocket data
        plt.pause(0.01)  # Allow Matplotlib to update the plot

fig, ax = plt.subplots()

if __name__ == "__main__":
    asyncio.run(main())
