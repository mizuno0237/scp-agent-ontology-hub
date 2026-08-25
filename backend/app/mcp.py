"""MCP-style tool catalog over the public ontology slice.

An agent lists tools, then calls them. It does not scrape the whole graph.
This is not the internal SCP metadata MCP and does not talk to live IPS APIs.
"""

from __future__ import annotations

from typing import Any

from .actions import preview_action
from .loader import load_schema, lookup_object, materialize_graph, search_objects, walk_link

TOOLS: list[dict[str, Any]] = [
    {
        "name": "list_object_types",
        "description": "List typed things the agent can name.",
        "arguments": [],
    },
    {
        "name": "inspect_object_type",
        "description": "Read one object type: properties and named links.",
        "arguments": ["objectType"],
    },
    {
        "name": "lookup_object",
        "description": "Read one instance and its incident links.",
        "arguments": ["objectType", "objectId"],
    },
    {
        "name": "walk_link",
        "description": "Follow one named edge from an instance.",
        "arguments": ["objectType", "objectId", "linkType"],
    },
    {
        "name": "preview_action",
        "description": "Ask whether a write is allowed against the logic rules.",
        "arguments": ["actionId", "objectId"],
    },
    {
        "name": "search_objects",
        "description": "Find sample instances by a substring. Optional objectType narrows the scan.",
        "arguments": ["query", "objectType"],
    },
]


def list_tools() -> dict[str, Any]:
    return {"protocol": "mcp-style", "readOnly": True, "tools": TOOLS}


def _missing(*keys: str, args: dict[str, Any]) -> str | None:
    empty = [key for key in keys if not args.get(key)]
    return f"missing {', '.join(empty)}" if empty else None


def call_tool(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    args = arguments or {}
    schema = load_schema()
    graph = materialize_graph()

    if name == "list_object_types":
        types = [
            {"id": row["id"], "primaryKey": row.get("primaryKey"), "description": row.get("description")}
            for row in schema["objectTypes"]["objectTypes"]
        ]
        return {"ok": True, "tool": name, "result": types}

    if name == "inspect_object_type":
        fault = _missing("objectType", args=args)
        if fault:
            return {"ok": False, "tool": name, "error": fault}
        found = next((row for row in schema["objectTypes"]["objectTypes"] if row["id"] == args["objectType"]), None)
        if found is None:
            return {"ok": False, "tool": name, "error": f"unknown object type {args['objectType']}"}
        links = [
            row
            for row in schema["linkTypes"]["linkTypes"]
            if row["from"] == found["id"] or row["to"] == found["id"]
        ]
        return {"ok": True, "tool": name, "result": {**found, "links": links}}

    if name == "lookup_object":
        fault = _missing("objectType", "objectId", args=args)
        if fault:
            return {"ok": False, "tool": name, "error": fault}
        payload = lookup_object(str(args["objectType"]), str(args["objectId"]))
        if payload is None or payload["object"] is None:
            return {"ok": False, "tool": name, "error": "object not in sample graph"}
        return {"ok": True, "tool": name, "result": payload}

    if name == "walk_link":
        fault = _missing("objectType", "objectId", "linkType", args=args)
        if fault:
            return {"ok": False, "tool": name, "error": fault}
        payload = walk_link(str(args["objectType"]), str(args["objectId"]), str(args["linkType"]))
        if payload is None or payload["object"] is None:
            return {"ok": False, "tool": name, "error": "object not in sample graph"}
        return {"ok": True, "tool": name, "result": payload}

    if name == "preview_action":
        fault = _missing("actionId", args=args)
        if fault:
            return {"ok": False, "tool": name, "error": fault}
        result = preview_action(graph, str(args["actionId"]), args.get("objectId"))
        return {"ok": True, "tool": name, "result": result}

    if name == "search_objects":
        fault = _missing("query", args=args)
        if fault:
            return {"ok": False, "tool": name, "error": fault}
        object_type = str(args["objectType"]) if args.get("objectType") else None
        result = search_objects(str(args["query"]), object_type)
        return {"ok": True, "tool": name, "result": result}

    return {"ok": False, "tool": name, "error": f"unknown tool {name}"}
