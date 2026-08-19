import type { ActionPreview, GraphPayload, ObjectLookup, OntologySchema, WalkPayload } from "./types";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`${path} failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export function fetchOntology(): Promise<OntologySchema> {
  return getJson("/api/ontology");
}

export function fetchGraph(): Promise<GraphPayload> {
  return getJson("/api/graph");
}

export function fetchObject(objectType: string, objectId: string): Promise<ObjectLookup> {
  return getJson(`/api/objects/${encodeURIComponent(objectType)}/${encodeURIComponent(objectId)}`);
}

export function fetchWalk(objectType: string, objectId: string, linkType: string): Promise<WalkPayload> {
  return getJson(
    `/api/objects/${encodeURIComponent(objectType)}/${encodeURIComponent(objectId)}/walk/${encodeURIComponent(linkType)}`
  );
}

export async function previewAction(actionId: string, objectId: string | null): Promise<ActionPreview> {
  const response = await fetch("/api/actions/preview", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ actionId, objectId }),
  });
  if (!response.ok) {
    throw new Error(`preview failed (${response.status})`);
  }
  return response.json() as Promise<ActionPreview>;
}
