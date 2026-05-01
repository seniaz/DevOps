from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterator

import pymysql
import pymysql.cursors

log = logging.getLogger(__name__)


class Database:
    def __init__(
        self,
        host: str,
        port: int,
        name: str,
        user: str,
        password: str,
        connect_timeout: int = 5,
    ) -> None:
        self.host = host
        self.port = port
        self.name = name
        self.user = user
        self.password = password
        self.connect_timeout = connect_timeout

    def _connect(self) -> pymysql.Connection:
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.name,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
            charset="utf8mb4",
            connect_timeout=self.connect_timeout,
        )

    @contextmanager
    def cursor(self) -> Iterator[pymysql.cursors.DictCursor]:
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                yield cur
        finally:
            conn.close()

    def health_check(self) -> tuple[bool, str | None]:
        try:
            with self.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            return True, None
        except Exception as exc:
            log.warning("DB health check failed: %s", exc)
            return False, f"database unreachable: {exc.__class__.__name__}"
