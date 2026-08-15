import { useEffect, useMemo, useState } from "react";
import { fetchGraph, fetchOntology, previewAction } from "./api";
import { TYPE_STAMP, type ActionPreview, type GraphPayload, type OntologySchema } from "./types";

const TYPE_ORDER = ["Supplier", "PurchaseOrder", "OrderLine", "Shipment", "InventoryPolicy"] as const;

export function App() {
  const [schema, setSchema] = useState<OntologySchema | null>(null);
  const [graph, setGraph] = useState<GraphPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [typeId, setTypeId] = useState<string>("PurchaseOrder");
  const [objectId, setObjectId] = useState<string>("PO-2024-0001");
  const [actionId, setActionId] = useState<string>("ApprovePurchaseOrder");
  const [preview, setPreview] = useState<ActionPreview | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    Promise.all([fetchOntology(), fetchGraph()])
      .then(([nextSchema, nextGraph]) => {
        setSchema(nextSchema);
        setGraph(nextGraph);
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  const instanceIds = useMemo(() => {
    if (!graph) return [];
    if (typeId === "Supplier") return graph.instances.Supplier.map((row) => row.id);
    if (typeId === "PurchaseOrder") return graph.instances.PurchaseOrder.map((row) => row.order_id);
    if (typeId === "OrderLine") return graph.instances.OrderLine.map((row) => row.id);
    if (typeId === "Shipment") return graph.instances.Shipment.map((row) => row.order_id);
    return graph.instances.InventoryPolicy.map((row) => row.material_class);
  }, [graph, typeId]);

  const edges = useMemo(() => {
    if (!graph) return [];
    return graph.links.filter((link) => link.from === objectId || link.to === objectId);
  }, [graph, objectId]);

  async function runPreview() {
    setBusy(true);
    try {
      setPreview(await previewAction(actionId, objectId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "preview failed");
    } finally {
      setBusy(false);
    }
  }

  if (error) {
    return (
      <main className="sheet">
        <p className="fault">Runtime unreachable. Start the API on :8000 — {error}</p>
      </main>
    );
  }

  if (!schema || !graph) {
    return (
      <main className="sheet">
        <p className="muted">Loading typed world model…</p>
      </main>
    );
  }

  const selectedType = schema.objectTypes.objectTypes.find((row) => row.id === typeId);

  return (
    <div className="sheet">
      <header className="title-block">
        <div className="title-block__mark">
          <span>DWG</span>
          <strong>ONT-SC-01</strong>
        </div>
        <div className="title-block__copy">
          <p className="eyebrow">Public sample · synthetic POs only</p>
          <h1>Agent world model</h1>
          <p>
            Object types, links, logic rules, and actions. The agent names things here instead of
            inferring them from prompt text.
          </p>
        </div>
        <dl className="title-block__meta">
          <div>
            <dt>Domain</dt>
            <dd>{graph.domain}</dd>
          </div>
          <div>
            <dt>Instances</dt>
            <dd>{graph.instances.PurchaseOrder.length} PO</dd>
          </div>
          <div>
            <dt>Edges</dt>
            <dd>{graph.links.length}</dd>
          </div>
        </dl>
      </header>

      <section className="deck">
        <aside className="rail">
          <h2>Object types</h2>
          <ul>
            {TYPE_ORDER.map((id) => {
              const row = schema.objectTypes.objectTypes.find((item) => item.id === id);
              if (!row) return null;
              return (
                <li key={id}>
                  <button
                    type="button"
                    className={id === typeId ? "is-live" : undefined}
                    onClick={() => {
                      setTypeId(id);
                      const first =
                        id === "Supplier"
                          ? graph.instances.Supplier[0]?.id
                          : id === "PurchaseOrder"
                            ? graph.instances.PurchaseOrder[0]?.order_id
                            : id === "OrderLine"
                              ? graph.instances.OrderLine[0]?.id
                              : id === "Shipment"
                                ? graph.instances.Shipment[0]?.order_id
                                : graph.instances.InventoryPolicy[0]?.material_class;
                      if (first) setObjectId(first);
                    }}
                  >
                    <span className="stamp">{TYPE_STAMP[id]}</span>
                    <span>
                      <strong>{row.id}</strong>
                      <em>{row.properties.length} props</em>
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
          {selectedType ? <p className="type-note">{selectedType.description}</p> : null}
        </aside>

        <section className="ledger">
          <div className="ledger__head">
            <h2>Instance ledger</h2>
            <label>
              Row
              <select value={objectId} onChange={(event) => setObjectId(event.target.value)}>
                {instanceIds.map((id) => (
                  <option key={id} value={id}>
                    {id}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <table>
            <thead>
              <tr>
                <th>Link</th>
                <th>From</th>
                <th>To</th>
              </tr>
            </thead>
            <tbody>
              {edges.map((link) => (
                <tr key={`${link.type}-${link.from}-${link.to}`}>
                  <td>
                    <code>{link.type}</code>
                  </td>
                  <td>
                    <span className="stamp stamp--tiny">{TYPE_STAMP[link.fromType]}</span>
                    {link.from}
                  </td>
                  <td>
                    <span className="stamp stamp--tiny">{TYPE_STAMP[link.toType]}</span>
                    {link.to}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {edges.length === 0 ? <p className="muted">No edges on this row.</p> : null}
        </section>

        <section className="action-bay">
          <h2>Action preview</h2>
          <p>Rules gate the action. The agent asks before it writes.</p>
          <label>
            Action
            <select value={actionId} onChange={(event) => setActionId(event.target.value)}>
              {schema.actions.actions.map((action) => (
                <option key={action.id} value={action.id}>
                  {action.id}
                </option>
              ))}
            </select>
          </label>
          <button type="button" className="run" onClick={runPreview} disabled={busy}>
            {busy ? "Checking rules…" : "Preview against rules"}
          </button>
          {preview ? (
            <output className={preview.allowed ? "ok" : "no"}>
              <strong>{preview.allowed ? "Allowed" : "Blocked"}</strong>
              {preview.humanInTheLoop ? <span className="hitl">human in the loop</span> : null}
              <p>{preview.reason}</p>
              {preview.firedRules.length ? (
                <ul>
                  {preview.firedRules.map((rule) => (
                    <li key={rule}>{rule}</li>
                  ))}
                </ul>
              ) : (
                <p className="muted">No rule fired.</p>
              )}
            </output>
          ) : null}

          <h3>Logic rules</h3>
          <ol className="rules">
            {schema.logicRules.rules.map((rule) => (
              <li key={rule.id}>
                <code>{rule.id}</code>
                <span>{rule.text}</span>
              </li>
            ))}
          </ol>
        </section>
      </section>
    </div>
  );
}
