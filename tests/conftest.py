import os
import sys

import pymysql
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from mywebapp.db import Database  # noqa: E402
from mywebapp.app import create_app  # noqa: E402

TEST_DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
TEST_DB_PORT = int(os.environ.get("DB_PORT", "3306"))
TEST_DB_USER = os.environ.get("DB_USER", "testuser")
TEST_DB_PASSWORD = os.environ.get("DB_PASSWORD", "testpassword")
TEST_DB_NAME = os.environ.get("DB_NAME", "testdb")


@pytest.fixture(scope="session")
def raw_connection():
    conn = pymysql.connect(
        host=TEST_DB_HOST,
        port=TEST_DB_PORT,
        user=TEST_DB_USER,
        password=TEST_DB_PASSWORD,
        database=TEST_DB_NAME,
        autocommit=True,
    )
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def clean_db(raw_connection):
    cur = raw_connection.cursor()
    cur.execute("DROP TABLE IF EXISTS items")
    cur.execute("DROP TABLE IF EXISTS schema_version")
    cur.execute("""
        CREATE TABLE items (
            id        INT          NOT NULL AUTO_INCREMENT,
            name      VARCHAR(255) NOT NULL,
            quantity  INT          NOT NULL DEFAULT 0,
            created_at TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    cur.close()
    yield


@pytest.fixture
def db():
    return Database(
        host=TEST_DB_HOST,
        port=TEST_DB_PORT,
        name=TEST_DB_NAME,
        user=TEST_DB_USER,
        password=TEST_DB_PASSWORD,
    )


@pytest.fixture
def app(db):
    application = create_app(db)
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()
