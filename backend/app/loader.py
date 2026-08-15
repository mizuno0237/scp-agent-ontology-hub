from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import ontology_dir, sample_root

TIER_MAP = {"S级": "S", "A级": "A", "B级": "B", "C级": "C"}

SKU_CLASS = {
    "STL": "steel",
    "ELC": "electronics",
    "PKG": "packaging",
    "ALU": "aluminum",
    "HW": "hardware",
}

# Synthetic on-hand for the public sample. Not a warehouse extract.
ON_HAND = {
    "steel": 80,
    "electronics": 12,
    "packaging": 4,
    "aluminum": 40,
    "hardware": 200,
}

POLICIES = [
    {
        "material_class": "steel",
        "safety_stock": 40,
        "reorder_point": 60,
        "max_stock": 200,
    },
    {
        "material_class": "electronics",
        "safety_stock": 20,
        "reorder_point": 30,
        "max_stock": 80,
    },
    {
        "material_class": "packaging",
        "safety_stock": 10,
        "reorder_point": 16,
        "max_stock": 50,
    },
    {
        "material_class": "aluminum",
        "safety_stock": 25,
        "reorder_point": 35,
        "max_stock": 120,
    },
    {
        "material_class": "hardware",
        "safety_stock": 50,
        "reorder_point": 80,
        "max_stock": 400,
    },
]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_schema() -> dict[str, Any]:
    root = ontology_dir()
    return {
        "objectTypes": _read_json(root / "object-types.json"),
        "linkTypes": _read_json(root / "link-types.json"),
        "logicRules": _read_json(root / "logic-rules.json"),
        "actions": _read_json(root / "actions.json"),
        "pipeline": _read_json(root / "pipeline-mapping.json"),
    }


def _tier(raw: str) -> str:
    return TIER_MAP.get(raw, raw.replace("级", "") if raw else "")


def _sku_class(sku: str) -> str:
    prefix = sku.split("-", 1)[0]
    return SKU_CLASS.get(prefix, "unknown")


def materialize_graph() -> dict[str, Any]:
    orders = _read_json(sample_root() / "supplier_orders.json")
    suppliers: dict[str, dict[str, Any]] = {}
    purchase_orders: list[dict[str, Any]] = []
    lines: list[dict[str, Any]] = []
    shipments: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []

    for order in orders:
        supplier = order["supplier"]
        sid = supplier["id"]
        suppliers[sid] = {
            "id": sid,
            "name": supplier["name"],
            "tier": _tier(supplier.get("level", "")),
            "region": supplier.get("region", ""),
        }

        amount = sum(item.get("total", 0) for item in order.get("items", []))
        po = {
            "order_id": order["order_id"],
            "order_date": order["order_date"],
            "status": order["status"],
            "amount": amount,
        }
        purchase_orders.append(po)
        links.append(
            {
                "type": "HAS_SUPPLIER",
                "fromType": "PurchaseOrder",
                "from": order["order_id"],
                "toType": "Supplier",
                "to": sid,
            }
        )

        for item in order.get("items", []):
            line_id = f"{order['order_id']}:{item['sku']}"
            material_class = _sku_class(item["sku"])
            lines.append(
                {
                    "id": line_id,
                    "order_id": order["order_id"],
                    "sku": item["sku"],
                    "name": item.get("name", ""),
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "material_class": material_class,
                }
            )
            links.append(
                {
                    "type": "HAS_LINE",
                    "fromType": "PurchaseOrder",
                    "from": order["order_id"],
                    "toType": "OrderLine",
                    "to": line_id,
                }
            )
            links.append(
                {
                    "type": "GOVERNED_BY",
                    "fromType": "OrderLine",
                    "from": line_id,
                    "toType": "InventoryPolicy",
                    "to": material_class,
                }
            )

        logistics = order.get("logistics") or {}
        shipments.append(
            {
                "order_id": order["order_id"],
                "carrier": logistics.get("carrier", ""),
                "expected_days": logistics.get("expected_days"),
                "actual_days": logistics.get("actual_days"),
                "on_time": logistics.get("on_time"),
            }
        )
        links.append(
            {
                "type": "HAS_SHIPMENT",
                "fromType": "PurchaseOrder",
                "from": order["order_id"],
                "toType": "Shipment",
                "to": order["order_id"],
            }
        )

    policies = []
    for policy in POLICIES:
        row = dict(policy)
        row["on_hand"] = ON_HAND[policy["material_class"]]
        policies.append(row)

    return {
        "domain": "supply-chain-planning",
        "synthetic": True,
        "instances": {
            "Supplier": list(suppliers.values()),
            "PurchaseOrder": purchase_orders,
            "OrderLine": lines,
            "Shipment": shipments,
            "InventoryPolicy": policies,
        },
        "links": links,
    }
