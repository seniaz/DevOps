import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    host: str
    port: int
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str


def parse_args(argv: list[str] | None = None) -> Config:
    parser = argparse.ArgumentParser(
        prog="mywebapp",
        description="Simple Inventory web service (variant 14)",
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="address to bind to when not running under systemd socket activation "
        "(default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="port to bind to when not running under systemd socket activation "
        "(default: 5000)",
    )

    parser.add_argument("--db-host", default="127.0.0.1", help="database host")
    parser.add_argument("--db-port", type=int, default=3306, help="database port")
    parser.add_argument("--db-name", default="mywebapp", help="database name")
    parser.add_argument("--db-user", default="mywebapp", help="database user")
    parser.add_argument(
        "--db-password", default="", help="database password (default: empty)"
    )

    ns = parser.parse_args(argv)
    return Config(
        host=ns.host,
        port=ns.port,
        db_host=ns.db_host,
        db_port=ns.db_port,
        db_name=ns.db_name,
        db_user=ns.db_user,
        db_password=ns.db_password,
    )
