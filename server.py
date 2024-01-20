print("Running server.py...")

import eventlet
import socketio
from dotenv import load_dotenv
import os

def main():
    if not load_dotenv():
        print("Could not load .env file or it is empty. Please check if it exists and is readable.")
        exit(1)

    client_path = os.environ.get('CLIENT_PATH') or "browser-client/"
    http_bind_host = os.environ.get('HTTP_BIND_HOST') or "0.0.0.0"
    http_bind_port = int(os.environ.get('HTTP_BIND_PORT') or 5000)

    print("Starting server at http://" + http_bind_host + ":" + str(http_bind_port) + "...")
    sio = socketio.Server(cors_allowed_origins='*')
    app = socketio.WSGIApp(sio, static_files={'/': client_path})
    eventlet.wsgi.server(eventlet.listen((http_bind_host, http_bind_port)), app)

if __name__ == "__main__":
    main()
