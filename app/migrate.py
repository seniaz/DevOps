from __future__ import annotations

import argparse
import logging
import sys
from typing import Any

import pymysql
import pymysql.cursors


MIGRATIONS: list[str] = [

    """
    CREATE TABLE IF NOT EXISTS schema_version (
        version INT NOT NULL PRIMARY KEY,
        applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,

    """
    CREATE TABLE IF NOT EXISTS items (
        id        INT          NOT NULL AUTO_INCREMENT,
        name      VARCHAR(255) NOT NULL,
        quantity  INT          NOT NULL DEFAULT 0,
        created_at TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        INDEX idx_items_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
]


def _current_version(cur: Any) -> int:
    try:
        cur.execute("SELECT MAX(version) AS v FROM schema_version")
        row = cur.fetchone()
        return int(row["v"]) if row and row["v"] is not None else 0
    except pymysql.err.ProgrammingError:

        return 0


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="mywebapp DB migration")
    p.add_argument("--db-host", default="127.0.0.1")
    p.add_argument("--db-port", type=int, default=3306)
    p.add_argument("--db-name", default="mywebapp")
    p.add_argument("--db-user", default="mywebapp")
    p.add_argument("--db-password", default="")
    return p.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    log = logging.getLogger("migrate")
    args = _parse_args()

    log.info(
        "connecting to %s@%s:%d/%s",
        args.db_user, args.db_host, args.db_port, args.db_name,
    )
    conn = pymysql.connect(
        host=args.db_host,
        port=args.db_port,
        user=args.db_user,
        password=args.db_password,
        database=args.db_name,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        charset="utf8mb4",
        connect_timeout=10,
    )

    try:
        with conn.cursor() as cur:
            current = _current_version(cur)
            target = len(MIGRATIONS)
            log.info("current schema version=%d, target=%d", current, target)

            for idx, sql in enumerate(MIGRATIONS, start=1):
                if idx <= current:
                    log.info("migration %d already applied — skipping", idx)
                    continue
                log.info("applying migration %d", idx)
                cur.execute(sql)
                cur.execute(
                    "INSERT INTO schema_version (version) VALUES (%s)",
                    (idx,),
                )
            log.info("schema is at version %d", target)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
