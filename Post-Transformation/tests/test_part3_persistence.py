from reliability_lab.persistence import LocalCheckpointStore
from reliability_lab.faults import FaultInjector, FaultPlan
from reliability_lab.models import FaultMode
import pytest

def test_checkpoint_survives_new_store_instance(tmp_path):
    path = tmp_path / "checkpoints.json"
    LocalCheckpointStore(path=path).save(
        "cp-001",
        {"request_id": "r1", "stage": "STARTED", "customer_id": "CUST-1"},
    )
    recovered = LocalCheckpointStore(path=path).load("cp-001")
    assert recovered["stage"] == "STARTED"
    assert recovered["customer_id"] == "CUST-1"

def test_persistence_failure_is_injectable(tmp_path):
    faults = FaultInjector(FaultPlan(FaultMode.PERSISTENCE_FAILURE))
    store = LocalCheckpointStore(path=tmp_path / "x.json", faults=faults)
    with pytest.raises(Exception):
        store.save("cp-fail", {"stage": "STARTED"})
