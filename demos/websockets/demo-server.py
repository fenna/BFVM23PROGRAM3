import asyncio
import json
import numpy as np
from websockets.asyncio.server import serve


async def send_data(websocket):
    t = 0  
    while True:
        noise = np.random.normal(0, 0.1)  
        sine_value = np.sin(2 * np.pi * 0.1 * t) + noise  
        data = {"time": t, "value": sine_value}
        await websocket.send(json.dumps(data))
        t += 1  
        await asyncio.sleep(0.1)  

async def main():
    async with serve(send_data, "localhost", 8765) as server:
        print('server started at port 8765')
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
