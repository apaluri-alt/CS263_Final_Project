# Made with ChatGPT.

import logging
import random
import time

from flask import Flask, jsonify
from werkzeug.serving import make_server


def serve(delay, connection, finished):
    """Signal readiness, then serve GET /packet until stopped."""
    app = Flask(__name__)

    @app.get("/packet")
    def get_packet():
        time.sleep(delay)
        return jsonify({"type": random.choice(["tcp", "udp"])})

    # Server threads let independent response delays overlap for every client model.
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    with make_server("127.0.0.1", 5000, app, threaded=True) as server:
        server.timeout = 0.05
        connection.send(True)
        connection.close()
        while not finished.is_set():
            server.handle_request()
