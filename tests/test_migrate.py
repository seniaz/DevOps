import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

import pymysql
from migrate import main as run_migration

TEST_DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
TEST_DB_PORT = int(os.environ.get("DB_PORT", "3306"))
TEST_DB_USER = os.environ.get("DB_USER", "testuser")
TEST_DB_PASSWORD = os.environ.get("DB_PASSWORD", "testpassword")
TEST_DB_NAME = os.environ.get("DB_NAME", "testdb")


def _connect():
    return pymysql.connect(
        host=TEST_DB_HOST,
        port=TEST_DB_PORT,
        user=TEST_DB_USER,
        password=TEST_DB_PASSWORD,
        database=TEST_DB_NAME,
        autocommit=True,
    )


def test_migration_creates_tables():
    conn = _connect()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS items")
    cur.execute("DROP TABLE IF EXISTS schema_version")
    cur.close()
    conn.close()

    sys.argv = [
        "migrate.py",
        "--db-host", TEST_DB_HOST,
        "--db-port", str(TEST_DB_PORT),
        "--db-user", TEST_DB_USER,
        "--db-password", TEST_DB_PASSWORD,
        "--db-name", TEST_DB_NAME,
    ]
    result = run_migration()
    assert result == 0

    conn = _connect()
    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    tables = [row[0] for row in cur.fetchall()]
    assert "items" in tables
    assert "schema_version" in tables
    cur.close()
    conn.close()


def test_migration_is_idempotent():
    sys.argv = [
        "migrate.py",
        "--db-host", TEST_DB_HOST,
        "--db-port", str(TEST_DB_PORT),
        "--db-user", TEST_DB_USER,
        "--db-password", TEST_DB_PASSWORD,
        "--db-name", TEST_DB_NAME,
    ]
    assert run_migration() == 0
    assert run_migration() == 0
