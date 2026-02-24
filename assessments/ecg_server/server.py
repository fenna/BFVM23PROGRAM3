import argparse
import asyncio
from typing import List
import websockets
from prompt_toolkit.enums import DEFAULT_BUFFER

DEFAULT_HOSTNAME = "localhost"
DEFAULT_PORT = 8080
DEFAULT_FILE_PATH = "Person1.csv"


async def send_data_with_delay(
    lines: List[str],
    websocket,
    delay: float = 0.1
) -> None:
    """
    Send lines of text to a WebSocket client with a fixed delay between messages.
    This function should not suffer from accumulated time drift. It tries to ensure that each
    message is send at the correct scheduled time, taking into account time taken to send
    previous messages.

    Args:
        lines (List[str]): Sequence of text lines to be sent to the client.
        websocket (WebSocketServerProtocol): Active WebSocket connection used for sending data.
        delay (float, optional): Time in seconds to wait between sending each line.
            Defaults to 0.1 seconds.

    Raises:
        websockets.exceptions.ConnectionClosed: If the client disconnects during transmission.
    """
    loop = asyncio.get_running_loop()
    start_time = loop.time()

    for i, line in enumerate(lines):
        # Calculate the exact scheduled time for this message
        scheduled_time = start_time + i * delay

        # Sleep only until the scheduled time (if we're ahead of schedule)
        now = loop.time()
        if scheduled_time > now:
            await asyncio.sleep(scheduled_time - now)

        await websocket.send(line)


async def handle_connection(websocket, file_path) -> None:
    """
    Handle an incoming WebSocket client connection.

    This function reads a CSV file from disk and streams its contents line-by-line
    to the connected client with a small delay between each message.

    Args:
        websocket: The connected WebSocket client.

    Raises:
        OSError: If the file cannot be read.
        Exception: Logs any unexpected runtime errors.
    """
    print("Client connected")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        await send_data_with_delay(lines, websocket)

    except Exception as e:
        print("Error:", e)


async def main(hostname, port, file_path) -> None:
    """
    Start the WebSocket server and keep it running indefinitely.

    The server listens on localhost at the configured PORT and handles
    incoming connections using `handle_connection`.
    """
    async with websockets.serve(
        lambda ws, _: handle_connection(ws, file_path), hostname, port
    ):
        print(f"WebSocket server running on {hostname}:{port} streaming '{file_path}'")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simple WebSocket server that streams a CSV file line by line."
    )
    parser.add_argument(
        "--host",
        type=str,
        default=DEFAULT_HOSTNAME,
        help=f"Hostname to listen on (default: {DEFAULT_HOSTNAME})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port to listen on (default: {DEFAULT_PORT})"
    )
    parser.add_argument(
        "--path",
        type=str,
        default=DEFAULT_FILE_PATH,
        help=f"Path to the CSV file (default: {DEFAULT_FILE_PATH})"
    )

    args = parser.parse_args()
    asyncio.run(main(args.host, args.port, args.path))