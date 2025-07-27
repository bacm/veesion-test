from datetime import datetime

import json
import os
import asyncio
import aiohttp
import aio_pika

from app.db import save_video

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"

QUEUE_NAME = "alerts"
VIDEO_SERVER = os.environ.get("VIDEO_SERVER", "http://nginx")

async def get_video_resolution_remote(video_path: str, header_bytes: int = 4 * 1024 * 1024):
    """
    Get video resolution from remote file by streaming only the headers.
    """
    url = f"{VIDEO_SERVER}{video_path}"
    headers = {"Range": f"bytes=0-{header_bytes - 1}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status not in (200, 206):
                raise RuntimeError(f"Failed to fetch video headers {url}: {resp.status}")
            data = await resp.read()

    # Run ffprobe via stdin (pipe)
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json",
        "pipe:0"  # Read input from stdin
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate(input=data)
    if process.returncode != 0:
        raise RuntimeError(f"ffprobe error: {stderr.decode()}")

    metadata = json.loads(stdout.decode())
    stream = metadata.get("streams", [{}])[0]
    return stream.get("width"), stream.get("height")


async def process_alert(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            alert = json.loads(message.body)
            print(f"[+] Received alert: {alert}")
            width, height = await get_video_resolution_remote(alert["video"])
            await save_video(alert["uid"], alert["video"], width, height)
            store = alert.get("store", "unknown")
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")   
            print(f"[Notification] Store: {store} | Date: {now} | Resolution: {width}x{height}")
        except Exception as e:
            print(f"Error processing alert: {e}")


async def main():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)

        print(" [*] Waiting for alerts. To exit press CTRL+C")
        await queue.consume(process_alert)

        # Keep the loop running forever
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
