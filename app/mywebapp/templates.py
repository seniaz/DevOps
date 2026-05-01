from __future__ import annotations

from html import escape
from typing import Iterable, Mapping


def render_root(endpoints: Iterable[tuple[str, str, str]]) -> str:
    rows = "\n".join(
        f"    <tr><td>{escape(method)}</td>"
        f"<td>{escape(path)}</td>"
        f"<td>{escape(desc)}</td></tr>"
        for method, path, desc in endpoints
    )
    return (
        "<!DOCTYPE html>\n"
        "<html><head><meta charset='utf-8'>"
        "<title>Simple Inventory</title></head>\n"
        "<body>\n"
        "<h1>Simple Inventory Service</h1>\n"
        "<p>Variant 14. See the endpoints exposed by the API below.</p>\n"
        "<h2>Endpoints</h2>\n"
        "<table border='1' cellpadding='4'>\n"
        "    <tr><th>Method</th><th>Path</th><th>Description</th></tr>\n"
        f"{rows}\n"
        "</table>\n"
        "</body></html>\n"
    )


def render_items_list(items: Iterable[Mapping[str, object]]) -> str:
    items = list(items)
    if not items:
        body = "<p>No items.</p>"
    else:
        rows = "\n".join(
            f"    <tr><td>{int(it['id'])}</td>"
            f"<td>{escape(str(it['name']))}</td></tr>"
            for it in items
        )
        body = (
            "<table border='1' cellpadding='4'>\n"
            "    <tr><th>ID</th><th>Name</th></tr>\n"
            f"{rows}\n"
            "</table>"
        )
    return (
        "<!DOCTYPE html>\n"
        "<html><head><meta charset='utf-8'>"
        "<title>Items</title></head>\n"
        "<body>\n"
        "<h1>Inventory items</h1>\n"
        f"{body}\n"
        "</body></html>\n"
    )


def render_item_detail(item: Mapping[str, object]) -> str:
    return (
        "<!DOCTYPE html>\n"
        "<html><head><meta charset='utf-8'>"
        f"<title>Item {int(item['id'])}</title></head>\n"
        "<body>\n"
        "<h1>Item details</h1>\n"
        "<table border='1' cellpadding='4'>\n"
        f"    <tr><th>ID</th><td>{int(item['id'])}</td></tr>\n"
        f"    <tr><th>Name</th><td>{escape(str(item['name']))}</td></tr>\n"
        f"    <tr><th>Quantity</th><td>{int(item['quantity'])}</td></tr>\n"
        f"    <tr><th>Created at</th>"
        f"<td>{escape(str(item['created_at']))}</td></tr>\n"
        "</table>\n"
        "</body></html>\n"
    )
