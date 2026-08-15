from app.actions import preview_action
from app.loader import load_schema, materialize_graph
from app.main import app
from fastapi.testclient import TestClient


def test_schema_has_four_blocks() -> None:
    schema = load_schema()
    assert schema["objectTypes"]["objectTypes"]
    assert schema["linkTypes"]["linkTypes"]
    assert schema["logicRules"]["rules"]
    assert schema["actions"]["actions"]


def test_graph_materializes_sample_pos() -> None:
    graph = materialize_graph()
    ids = {row["order_id"] for row in graph["instances"]["PurchaseOrder"]}
    assert "PO-2024-0001" in ids
    assert "PO-2024-0003" in ids
    assert graph["synthetic"] is True


def test_approve_po_fires_amount_rule() -> None:
    graph = materialize_graph()
    result = preview_action(graph, "ApprovePurchaseOrder", "PO-2024-0001")
    assert result["allowed"] is True
    assert result["humanInTheLoop"] is True
    assert "PO_APPROVAL_BY_AMOUNT" in result["firedRules"]


def test_late_shipment_can_be_flagged() -> None:
    graph = materialize_graph()
    result = preview_action(graph, "FlagLateShipment", "PO-2024-0003")
    assert result["allowed"] is True
    assert "SUPPLIER_TIER_DOWNGRADE" in result["firedRules"]


def test_packaging_is_below_safety() -> None:
    graph = materialize_graph()
    result = preview_action(graph, "CreateReplenishmentRequest", "packaging")
    assert result["allowed"] is True
    assert "EMERGENCY_BUY" in result["firedRules"]


def test_health() -> None:
    client = TestClient(app)
    assert client.get("/health").json()["ok"] is True
