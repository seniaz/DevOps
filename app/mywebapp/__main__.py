from __future__ import annotations

import logging

from .app import create_app
from .config import parse_args
from .db import Database
from .server import run


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    cfg = parse_args()
    db = Database(
        host=cfg.db_host,
        port=cfg.db_port,
        name=cfg.db_name,
        user=cfg.db_user,
        password=cfg.db_password,
    )
    app = create_app(db)
    run(app, host=cfg.host, port=cfg.port)


if __name__ == "__main__":
    main()
