import asyncio
import websockets

# Define the WebSocket server handler
async def echo(websocket, path):
    async for message in websocket:
        # Echo the received message back to the client
        await websocket.send(message)

# Start the WebSocket server
start_server = websockets.serve(echo, "localhost", 8765)

# Run the server indefinitely
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

