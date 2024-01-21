#!/usr/bin/env python3
print("Running server.py...")

import eventlet
import socketio
import dotenv
import os
import json

# The above imports are for libraries. In order to import files (like query.py), we write:
import query

client_path = os.environ.get("CLIENT_PATH") or "browser-client/"
http_bind_host = os.environ.get("HTTP_BIND_HOST") or "0.0.0.0"
http_bind_port = int(os.environ.get("HTTP_BIND_PORT") or 5000)

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio, static_files={"/": client_path})

def main():
    if not dotenv.load_dotenv():
        print("Could not load .env file or it is empty. Please check if it exists and is readable.")
        exit(1)

    query.init()

    eventlet.wsgi.server(eventlet.listen((http_bind_host, http_bind_port)), app)

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
def disconnect(sid):
    print("disconnect ", sid)

def generate_sid():
    """Generate a random string of length 10."""
    import random
    import string
    return ''.join(random.choice(string.ascii_letters) for i in range(10))

@sio.event
def message(sid, data):
    # Random string
    message_sid = generate_sid()
    client_message = json.loads(data)

    first_reply = {
        "kind": "first_reply",
        "text": f"Ok, we received your message: {client_message.get('text')}",
        "message_sid": message_sid,
        "isNewMessage": True,
    }

    sio.emit("message", json.dumps(first_reply))

    llm_output = query.query(client_message.get("text"))
    second_reply = {
        "kind": "second_reply",
        "llm_output": llm_output,
        "message_sid": message_sid,
        "isNewMessage": True,
    }

    sio.emit("message", json.dumps(second_reply))

if __name__ == "__main__":
    main()
