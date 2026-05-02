from __future__ import annotations

import logging
from typing import Any

from flask import Flask, Response, abort, jsonify, request

from .db import Database
from .templates import render_item_detail, render_items_list, render_root

log = logging.getLogger(__name__)


BUSINESS_ENDPOINTS: list[tuple[str, str, str]] = [
    ("GET", "/items", "List all inventory items"),
    ("POST", "/items", "Create a new inventory item"),
    ("GET", "/items/<id>", "Get details of a specific item"),
]


def _wants_html() -> bool:
    accept = request.headers.get("Accept", "")
    return "text/html" in accept


def _serialize_item(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    if out.get("created_at") is not None:
        out["created_at"] = out["created_at"].isoformat()
    return out


def create_app(db: Database) -> Flask:
    app = Flask(__name__)

    app.json.sort_keys = False


    @app.get("/")
    def root() -> Response:
        accept = request.headers.get("Accept", "*/*")

        if (
            "text/html" not in accept
            and "*/*" not in accept
            and accept.strip() != ""
        ):
            abort(406, description="root endpoint serves only text/html")
        return Response(render_root(BUSINESS_ENDPOINTS), mimetype="text/html")


    @app.get("/health/alive")
    def alive() -> Response:
        return Response("OK", mimetype="text/plain")

    @app.get("/health/ready")
    def ready() -> Response:
        ok, err = db.health_check()
        if ok:
            return Response("OK", mimetype="text/plain")
        return Response(
            err or "not ready",
            status=500,
            mimetype="text/plain",
        )


    @app.get("/items")
    def list_items() -> Response:
        with db.cursor() as cur:
            cur.execute("SELECT id, name FROM items ORDER BY id")
            rows = cur.fetchall()
        if _wants_html():
            return Response(render_items_list(rows), mimetype="text/html")
        return jsonify(rows)

    @app.post("/items")
    def create_item() -> Response:

        if request.is_json:
            data = request.get_json(silent=True) or {}
        else:
            data = request.form.to_dict()

        name = data.get("name")
        quantity = data.get("quantity", 0)

        if not name or not isinstance(name, str):
            abort(400, description="'name' is required and must be a string")
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            abort(400, description="'quantity' must be an integer")
        if quantity < 0:
            abort(400, description="'quantity' must be >= 0")

        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO items (name, quantity) VALUES (%s, %s)",
                (name, quantity),
            )
            new_id = cur.lastrowid
            cur.execute(
                "SELECT id, name, quantity, created_at FROM items WHERE id = %s",
                (new_id,),
            )
            row = cur.fetchone()

        if row is None:
            abort(500, description="failed to read inserted item back")

        item = _serialize_item(row)
        if _wants_html():
            return Response(
                render_item_detail(row),
                status=201,
                mimetype="text/html",
            )
        resp = jsonify(item)
        resp.status_code = 201
        return resp

    @app.get("/items/<int:item_id>")
    def get_item(item_id: int) -> Response:
        with db.cursor() as cur:
            cur.execute(
                "SELECT id, name, quantity, created_at FROM items WHERE id = %s",
                (item_id,),
            )
            row = cur.fetchone()
        if row is None:
            abort(404, description="item not found")
        if _wants_html():
            return Response(render_item_detail(row), mimetype="text/html")
        return jsonify(_serialize_item(row))


    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(406)
    @app.errorhandler(500)
    def _err(e):
        code = getattr(e, "code", 500)
        msg = getattr(e, "description", str(e))
        if _wants_html():
            return Response(
                f"<h1>{code}</h1><p>{msg}</p>",
                status=code,
                mimetype="text/html",
            )
        return jsonify({"error": msg, "status": code}), code

    return app
