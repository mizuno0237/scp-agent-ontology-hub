from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .actions import preview_action
from .loader import load_schema, lookup_object, materialize_graph

app = FastAPI(
    title="SCP Agent Ontology Hub",
    description="Sanitized public slice: typed world model for a planning agent.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PreviewBody(BaseModel):
    actionId: str
    objectId: str | None = Field(default=None)


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True, "slice": "public-sample", "graph": "sqlite-free-json"}


@app.get("/api/ontology")
def ontology() -> dict[str, Any]:
    return load_schema()


@app.get("/api/graph")
def graph() -> dict[str, Any]:
    return materialize_graph()


@app.get("/api/objects/{object_type}/{object_id:path}")
def object_lookup(object_type: str, object_id: str) -> dict[str, Any]:
    payload = lookup_object(object_type, object_id)
    if payload is None:
        raise HTTPException(status_code=404, detail=f"Unknown object type {object_type}")
    if payload["object"] is None:
        raise HTTPException(status_code=404, detail=f"{object_type} {object_id} is not in the sample graph")
    return payload


@app.post("/api/actions/preview")
def actions_preview(body: PreviewBody) -> dict[str, Any]:
    if not body.actionId:
        raise HTTPException(status_code=400, detail="actionId is required")
    return preview_action(materialize_graph(), body.actionId, body.objectId)
