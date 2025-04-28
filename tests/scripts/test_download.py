import asyncio
import json

async def download_file():
    reader, writer = await asyncio.open_connection('127.0.0.1', 6000)

    # Create a dummy download file request
    message = {
        "type": "request",
        "action": "file_download",
        "peer_info": {"host": "127.0.0.1", "port": 6000},  # client info (dummy)
        "data": {"filename": "uwu.txt"}  # file to request
    }
    # Your protocol uses Latin1 encoding and bytes
    message_bytes = json.dumps(message).encode()

    writer.write(message_bytes)
    await writer.drain()

    response = await reader.read()
    print("Response from peer:", response.decode())

    writer.close()
    await writer.wait_closed()

asyncio.run(download_file())
