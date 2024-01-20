print("Running server.py...")

import eventlet
import socketio
import dotenv
import os
import json

client_path = os.environ.get("CLIENT_PATH") or "browser-client/"
http_bind_host = os.environ.get("HTTP_BIND_HOST") or "0.0.0.0"
http_bind_port = int(os.environ.get("HTTP_BIND_PORT") or 5000)

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio, static_files={"/": client_path})

def main():
    if not dotenv.load_dotenv():
        print("Could not load .env file or it is empty. Please check if it exists and is readable.")
        exit(1)

    eventlet.wsgi.server(eventlet.listen((http_bind_host, http_bind_port)), app)

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
def disconnect(sid):
    print("disconnect ", sid)

@sio.event
def message(sid, data):
    message = json.loads(data)

    reply = {
        "text": f"Ok, we received your message: {message.get('text')}",
        "message_sid": message.get("message_sid"),
        "isNewMessage": True,
    }
    sio.emit("message", json.dumps(reply), room=sid)

if __name__ == "__main__":
    main()
