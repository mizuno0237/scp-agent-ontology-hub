# Supply-chain sample ontology

Typed world model for the synthetic files in `samples/supply-chain/`. An agent should speak these names instead of free-text columns.

| File | Building block |
| --- | --- |
| `object-types.json` | Entity / object types |
| `link-types.json` | Relation / link types |
| `logic-rules.json` | Constraints lifted from `supply_chain_strategy.md` |
| `actions.json` | Allowed writes (several require a human) |
| `pipeline-mapping.json` | How `supplier_orders.json` becomes objects and links |

Walk one record: `PO-2024-0001` → `PurchaseOrder` → `HAS_SUPPLIER` → `SUP-001` → `HAS_LINE` → `STL-001` / `STL-002` → `HAS_SHIPMENT` (on time).

Runtime that loads this folder is a later slice. This commit is the mapping, not the GitLab app.
