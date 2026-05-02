from __future__ import annotations

import logging
import os
import socket
from typing import Callable

from werkzeug.serving import make_server


SD_LISTEN_FDS_START = 3

log = logging.getLogger(__name__)


def _systemd_socket() -> socket.socket | None:
    listen_pid = os.environ.get("LISTEN_PID")
    listen_fds = os.environ.get("LISTEN_FDS")
    if not listen_pid or not listen_fds:
        return None
    try:
        if int(listen_pid) != os.getpid():
            return None
        n_fds = int(listen_fds)
    except ValueError:
        return None
    if n_fds < 1:
        return None

    return socket.socket(
        fileno=SD_LISTEN_FDS_START,
        family=socket.AF_INET,
        type=socket.SOCK_STREAM,
    )


def run(app: Callable, host: str, port: int) -> None:
    sock = _systemd_socket()
    if sock is not None:
        bound = sock.getsockname()
        log.info("Using systemd socket activation, inherited fd=%d (bound to %s)",
                 SD_LISTEN_FDS_START, bound)

        server = make_server(
            host=bound[0],
            port=bound[1],
            app=app,
            threaded=True,
            fd=SD_LISTEN_FDS_START,
        )
    else:
        log.info("Binding to %s:%d (no socket activation)", host, port)
        server = make_server(host=host, port=port, app=app, threaded=True)
    log.info("mywebapp ready, serving requests")
    server.serve_forever()
