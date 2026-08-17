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


def test_object_lookup_returns_po_and_incident_links() -> None:
    client = TestClient(app)
    payload = client.get("/api/objects/PurchaseOrder/PO-2024-0001").json()
    assert payload["object"]["order_id"] == "PO-2024-0001"
    assert payload["primaryKey"] == "order_id"
    types = {link["type"] for link in payload["links"]}
    assert "HAS_SUPPLIER" in types
    assert "HAS_SHIPMENT" in types


def test_object_lookup_404_for_unknown_type() -> None:
    client = TestClient(app)
    response = client.get("/api/objects/WorkOrder/WO-1842")
    assert response.status_code == 404


def test_object_lookup_404_for_missing_id() -> None:
    client = TestClient(app)
    response = client.get("/api/objects/PurchaseOrder/PO-MISSING")
    assert response.status_code == 404
