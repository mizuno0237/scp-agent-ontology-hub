# Agent Ontology Hub

The **ontology layer an agent uses as its world model**: object types, relations, logic rules, and executable actions. First public sample domain: **supply chain planning** (suppliers, purchase orders, inventory policies).

This is a **sanitized public slice**, not a mirror of any internal GitLab. Internal hostnames, private registries, production compose files, and real customer masters are stripped.

Inspired by Palantir-style ontology platforms and the open-source [nano-ontoprompt](https://github.com/jingw2/nano-ontoprompt) architecture (Pipeline Mapping + LLM extraction).

| Building block | Role for an agent |
| --- | --- |
| **Entity (object type)** | Typed things the agent can name (`Supplier`, `PurchaseOrder`) |
| **Relation (link type)** | Typed edges (`PurchaseOrder -HAS_SUPPLIER-> Supplier`) |
| **Logic rule** | Constraints and state machines the agent must respect |
| **Action** | Allowed operations (`Approve Record`, `Link Order to Supplier`) |

## What is in this D1 snapshot

- English positioning README
- `.env.example` (placeholders only)
- Public-image `docker-compose.v2.yml` (no private registry)
- Synthetic supply-chain sample under `samples/supply-chain/`

Runtime (FastAPI + React) lands in D2 after secret scan. Do **not** expect `docker compose up` to serve the full app from D1 alone.

## Quick start (env only)

```bash
cp .env.example .env
# fill keys locally; never commit .env
```

## License

MIT
