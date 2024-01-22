#!/usr/bin/env python3
print("Running server.py...")

import socketio
import dotenv
import os
import json
import uvicorn
import query

# Load environment variables
if not dotenv.load_dotenv():
    print("Could not load .env file or it is empty. Please check if it exists and is readable.")
    exit(1)

client_path = os.environ.get("CLIENT_PATH") or "browser-client/"
http_bind_host = os.environ.get("HTTP_BIND_HOST") or "0.0.0.0"
http_bind_port = int(os.environ.get("HTTP_BIND_PORT") or 5000)

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
app = socketio.ASGIApp(sio, static_files={"/": client_path})

async def ping_clients():
    while True:
        await asyncio.sleep(2)  # Ping interval
        for sid in connected_sids:
            await sio.emit('ping', {'data': 'ping'}, room=sid)

async def main():
    query.init()
    config = uvicorn.Config(app=app, host=http_bind_host, port=http_bind_port)
    server = uvicorn.Server(config)
    asyncio.create_task(ping_clients())
    await server.serve()

connected_sids = set()

@sio.event
async def connect(sid, environ):
    print("connect ", sid)
    connected_sids.add(sid)

@sio.event
async def disconnect(sid):
    print("disconnect ", sid)
    connected_sids.remove(sid)

def generate_sid():
    import random
    import string
    return ''.join(random.choice(string.ascii_letters) for i in range(10))

@sio.event
async def message(sid, data):
    message_sid = generate_sid()
    client_message = json.loads(data)

    first_reply = {
        "kind": "first_reply",
        "text": f"Ok, we received your message: {client_message.get('text')}",
        "message_sid": message_sid,
    }
    await sio.emit("message", json.dumps(first_reply))

    print(first_reply)

    # Yield control to the event loop so that the client can receive the first reply
    await asyncio.sleep(0)

    # Start the long-running task in the background
    task = asyncio.create_task(process_query(client_message.get("text"), message_sid))

    await asyncio.sleep(0)

    await task


async def process_query(text, message_sid):
    loop = asyncio.get_running_loop()

    # Define a wrapper function for the coroutine
    def query_sync():
        return asyncio.run(query.query(text))

    llm_output = await loop.run_in_executor(None, query_sync)


    # Once the blocking task is done, emit the results
    second_reply = {
        "kind": "second_reply",
        "text": llm_output.get("reply"),
        "message_sid": message_sid,
    }
    await sio.emit("message", json.dumps(second_reply))

    for doc in llm_output.get("source_documents"):
        doc_reply = {
            "kind": "source_document",
            "source": doc.get("source"),
            "text": doc.get("content"),
            "message_sid": message_sid,
        }
        await sio.emit("message", json.dumps(doc_reply))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
