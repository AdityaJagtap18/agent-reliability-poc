import uuid
from reliability_lab.agent import ReliabilityAgent
from reliability_lab.faults import FaultInjector, FaultPlan
from reliability_lab.models import AgentRequest, FaultMode

def req():
    return AgentRequest(str(uuid.uuid4()), "CUST-1001", "What is the customer's status?")

def test_tool_timeout_is_contained():
    result = ReliabilityAgent(
        faults=FaultInjector(FaultPlan(FaultMode.TOOL_TIMEOUT, trigger_count=5)),
        use_azure=False,
    ).run(req())
    assert result.status == "ESCALATED"
    assert result.escalated

def test_llm_timeout_is_bounded_and_safe():
    result = ReliabilityAgent(
        faults=FaultInjector(FaultPlan(FaultMode.LLM_TIMEOUT, trigger_count=5)),
        use_azure=False,
    ).run(req())
    assert result.retries == 2
    assert result.status == "DEGRADED"
    assert result.escalated
    assert "temporarily unavailable" in result.answer

def test_rate_limit_is_bounded():
    result = ReliabilityAgent(
        faults=FaultInjector(FaultPlan(FaultMode.LLM_RATE_LIMIT, trigger_count=5)),
        use_azure=False,
    ).run(req())
    assert result.retries == 2
    assert result.status == "DEGRADED"

def test_cascade_failure_is_contained():
    result = ReliabilityAgent(
        faults=FaultInjector(FaultPlan(FaultMode.CASCADE_FAILURE, trigger_count=5)),
        use_azure=False,
    ).run(req())
    assert result.status == "ESCALATED"
    assert result.escalated
