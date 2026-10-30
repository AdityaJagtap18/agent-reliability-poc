import uuid
from reliability_lab.agent import ReliabilityAgent
from reliability_lab.models import AgentRequest
from reliability_lab.scoring import score

def test_successful_run_has_events_and_checkpoint():
    result = ReliabilityAgent(use_azure=False).run(
        AgentRequest(str(uuid.uuid4()), "CUST-1001", "Give me a status.")
    )
    assert result.status == "SUCCESS"
    assert result.checkpoint_id
    assert result.events
    assert 0 <= score(result).total <= 100
    assert score(result).observability > 0

def test_score_penalizes_missing_observability():
    result = ReliabilityAgent(use_azure=False).run(
        AgentRequest(str(uuid.uuid4()), "CUST-1001", "Give me a status.")
    )
    result.events = []
    assert score(result).observability == 5
