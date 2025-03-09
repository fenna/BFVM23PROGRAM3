import asyncio
import websockets
import pandas as pd
import json

df = pd.DataFrame(columns=["time", "value"])

async def receive_data():
    global df  
    async with websockets.connect("ws://localhost:8765") as websocket:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                
                df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

                print(df.tail(5))
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket closed")
                break

if __name__=='__main__':
    asyncio.run(receive_data())
