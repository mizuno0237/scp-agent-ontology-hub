from __future__ import annotations

from typing import Any


def preview_action(graph: dict[str, Any], action_id: str, object_id: str | None) -> dict[str, Any]:
    if action_id not in {
        "LinkOrderToSupplier",
        "ApprovePurchaseOrder",
        "CreateReplenishmentRequest",
        "FlagLateShipment",
    }:
        return {
            "actionId": action_id,
            "allowed": False,
            "humanInTheLoop": False,
            "reason": "Unknown action on this public sample.",
            "firedRules": [],
        }

    if action_id == "ApprovePurchaseOrder":
        return _approve_po(graph, object_id)
    if action_id == "FlagLateShipment":
        return _flag_late(graph, object_id)
    if action_id == "CreateReplenishmentRequest":
        return _replenish(graph, object_id)
    return _link_supplier(graph, object_id)


def _po(graph: dict[str, Any], order_id: str | None) -> dict[str, Any] | None:
    if not order_id:
        return None
    for row in graph["instances"]["PurchaseOrder"]:
        if row["order_id"] == order_id:
            return row
    return None


def _supplier_for(graph: dict[str, Any], order_id: str) -> dict[str, Any] | None:
    sid = None
    for link in graph["links"]:
        if link["type"] == "HAS_SUPPLIER" and link["from"] == order_id:
            sid = link["to"]
            break
    if not sid:
        return None
    for row in graph["instances"]["Supplier"]:
        if row["id"] == sid:
            return row
    return None


def _shipment(graph: dict[str, Any], order_id: str | None) -> dict[str, Any] | None:
    if not order_id:
        return None
    for row in graph["instances"]["Shipment"]:
        if row["order_id"] == order_id:
            return row
    return None


def _policy(graph: dict[str, Any], material_class: str | None) -> dict[str, Any] | None:
    if not material_class:
        return None
    for row in graph["instances"]["InventoryPolicy"]:
        if row["material_class"] == material_class:
            return row
    return None


def _approve_po(graph: dict[str, Any], order_id: str | None) -> dict[str, Any]:
    po = _po(graph, order_id)
    if not po:
        return {
            "actionId": "ApprovePurchaseOrder",
            "allowed": False,
            "humanInTheLoop": True,
            "reason": "Pick a purchase order first.",
            "firedRules": [],
        }
    amount = po["amount"]
    if amount >= 2_000_000:
        return {
            "actionId": "ApprovePurchaseOrder",
            "objectId": po["order_id"],
            "allowed": False,
            "humanInTheLoop": True,
            "reason": f"Amount {amount} is above the public sample ceiling.",
            "firedRules": ["PO_APPROVAL_VP"],
        }
    if amount >= 500_000:
        return {
            "actionId": "ApprovePurchaseOrder",
            "objectId": po["order_id"],
            "allowed": True,
            "humanInTheLoop": True,
            "reason": f"Amount {amount} needs supply-chain VP approval before the agent may submit.",
            "firedRules": ["PO_APPROVAL_VP"],
        }
    if amount >= 50_000:
        return {
            "actionId": "ApprovePurchaseOrder",
            "objectId": po["order_id"],
            "allowed": True,
            "humanInTheLoop": True,
            "reason": f"Amount {amount} needs manager approval. Agent must not fire submit yet.",
            "firedRules": ["PO_APPROVAL_BY_AMOUNT"],
        }
    return {
        "actionId": "ApprovePurchaseOrder",
        "objectId": po["order_id"],
        "allowed": True,
        "humanInTheLoop": False,
        "reason": f"Amount {amount} is under the clerk threshold.",
        "firedRules": [],
    }


def _flag_late(graph: dict[str, Any], order_id: str | None) -> dict[str, Any]:
    shipment = _shipment(graph, order_id)
    if not shipment:
        return {
            "actionId": "FlagLateShipment",
            "allowed": False,
            "humanInTheLoop": False,
            "reason": "Pick a purchase order that has a shipment.",
            "firedRules": [],
        }
    if shipment["on_time"] is True:
        return {
            "actionId": "FlagLateShipment",
            "objectId": shipment["order_id"],
            "allowed": False,
            "humanInTheLoop": False,
            "reason": "Receipt is on time. No late flag.",
            "firedRules": [],
        }
    if shipment["on_time"] is None:
        return {
            "actionId": "FlagLateShipment",
            "objectId": shipment["order_id"],
            "allowed": False,
            "humanInTheLoop": False,
            "reason": "Shipment is still in transit. Wait for the receipt.",
            "firedRules": [],
        }
    return {
        "actionId": "FlagLateShipment",
        "objectId": shipment["order_id"],
        "allowed": True,
        "humanInTheLoop": False,
        "reason": "Late receipt. Agent may flag and feed the supplier-tier state machine.",
        "firedRules": ["SUPPLIER_TIER_DOWNGRADE"],
    }


def _replenish(graph: dict[str, Any], material_class: str | None) -> dict[str, Any]:
    policy = _policy(graph, material_class)
    if not policy:
        return {
            "actionId": "CreateReplenishmentRequest",
            "allowed": False,
            "humanInTheLoop": True,
            "reason": "Pick an inventory policy (material class).",
            "firedRules": [],
        }
    on_hand = policy["on_hand"]
    safety = policy["safety_stock"]
    if on_hand < safety * 0.5:
        return {
            "actionId": "CreateReplenishmentRequest",
            "objectId": policy["material_class"],
            "allowed": True,
            "humanInTheLoop": True,
            "reason": f"On-hand {on_hand} is under half of safety {safety}. Escalate; skip clerk.",
            "firedRules": ["EMERGENCY_BUY", "REORDER_TRIGGER"],
        }
    if on_hand < safety:
        return {
            "actionId": "CreateReplenishmentRequest",
            "objectId": policy["material_class"],
            "allowed": True,
            "humanInTheLoop": True,
            "reason": f"On-hand {on_hand} is below safety {safety}. Agent proposes; planner confirms.",
            "firedRules": ["REORDER_TRIGGER"],
        }
    return {
        "actionId": "CreateReplenishmentRequest",
        "objectId": policy["material_class"],
        "allowed": False,
        "humanInTheLoop": True,
        "reason": f"On-hand {on_hand} is at or above safety {safety}.",
        "firedRules": [],
    }


def _link_supplier(graph: dict[str, Any], order_id: str | None) -> dict[str, Any]:
    po = _po(graph, order_id)
    if not po:
        return {
            "actionId": "LinkOrderToSupplier",
            "allowed": False,
            "humanInTheLoop": False,
            "reason": "Pick a purchase order first.",
            "firedRules": [],
        }
    supplier = _supplier_for(graph, po["order_id"])
    if not supplier:
        return {
            "actionId": "LinkOrderToSupplier",
            "objectId": po["order_id"],
            "allowed": False,
            "humanInTheLoop": False,
            "reason": "No supplier row on this order.",
            "firedRules": [],
        }
    if supplier["tier"] == "C":
        return {
            "actionId": "LinkOrderToSupplier",
            "objectId": po["order_id"],
            "allowed": False,
            "humanInTheLoop": False,
            "reason": f"{supplier['id']} is tier C (treated as suspended on this sample).",
            "firedRules": ["SUPPLIER_TIER_DOWNGRADE"],
        }
    return {
        "actionId": "LinkOrderToSupplier",
        "objectId": po["order_id"],
        "allowed": True,
        "humanInTheLoop": False,
        "reason": f"Write HAS_SUPPLIER to {supplier['id']} ({supplier['tier']}).",
        "firedRules": [],
    }
