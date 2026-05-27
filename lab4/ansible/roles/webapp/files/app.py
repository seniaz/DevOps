#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime

from flask import Flask, request, jsonify, make_response
import pymysql

app = Flask(__name__)
DB_CONFIG = {}


def get_db():
    return pymysql.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        cursorclass=pymysql.cursors.DictCursor,
    )


def run_migration():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    quantity INT NOT NULL DEFAULT 0,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()
    finally:
        conn.close()


def wants_json():
    return request.accept_mimetypes.best_match(["application/json", "text/html"]) == "application/json"


@app.route("/health/alive")
def health_alive():
    return "OK", 200


@app.route("/health/ready")
def health_ready():
    try:
        conn = get_db()
        conn.ping()
        conn.close()
        return "OK", 200
    except Exception as e:
        return f"NOT READY: {e}", 500


@app.route("/")
def index():
    html = """<html><body>
    <h1>Simple Inventory</h1>
    <ul>
      <li><a href="/items">GET /items</a></li>
      <li>POST /items</li>
      <li>GET /items/&lt;id&gt;</li>
    </ul>
    </body></html>"""
    return make_response(html, 200)


@app.route("/items", methods=["GET"])
def list_items():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM items ORDER BY id")
            rows = cur.fetchall()
    finally:
        conn.close()

    if wants_json():
        return jsonify(rows)

    table_rows = "".join(f"<tr><td>{r['id']}</td><td>{r['name']}</td></tr>" for r in rows)
    html = f"""<html><body>
    <h1>Items</h1>
    <table border='1'><tr><th>ID</th><th>Name</th></tr>{table_rows}</table>
    </body></html>"""
    return make_response(html, 200)


@app.route("/items", methods=["POST"])
def create_item():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    name = data.get("name")
    quantity = data.get("quantity", 0)

    if not name:
        return jsonify({"error": "name is required"}), 400

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO items (name, quantity) VALUES (%s, %s)",
                (name, int(quantity)),
            )
        conn.commit()
        item_id = cur.lastrowid
    finally:
        conn.close()

    result = {"id": item_id, "name": name, "quantity": int(quantity)}

    if wants_json():
        return jsonify(result), 201

    html = f"<html><body><p>Created item {item_id}: {name}</p><a href='/items'>Back</a></body></html>"
    return make_response(html, 201)


@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, quantity, created_at FROM items WHERE id = %s", (item_id,))
            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return jsonify({"error": "not found"}), 404

    row["created_at"] = row["created_at"].isoformat() if isinstance(row["created_at"], datetime) else str(row["created_at"])

    if wants_json():
        return jsonify(row)

    html = f"""<html><body>
    <h1>{row['name']}</h1>
    <p>ID: {row['id']}</p>
    <p>Quantity: {row['quantity']}</p>
    <p>Created: {row['created_at']}</p>
    <a href='/items'>Back</a>
    </body></html>"""
    return make_response(html, 200)


def main():
    parser = argparse.ArgumentParser(description="Simple Inventory Service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--db-host", default="127.0.0.1")
    parser.add_argument("--db-port", type=int, default=3306)
    parser.add_argument("--db-user", default="mywebapp")
    parser.add_argument("--db-password", default="")
    parser.add_argument("--db-name", default="mywebapp")
    args = parser.parse_args()

    DB_CONFIG.update({
        "host": args.db_host,
        "port": args.db_port,
        "user": args.db_user,
        "password": args.db_password,
        "database": args.db_name,
    })

    run_migration()
    app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
