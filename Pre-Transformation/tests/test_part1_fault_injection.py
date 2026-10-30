import pytest
from reliability_lab.faults import FaultInjector, FaultPlan, InjectedFault
from reliability_lab.models import FaultMode

@pytest.mark.parametrize("mode", list(FaultMode))
def test_each_fault_mode_is_injectable(mode):
    injector = FaultInjector(FaultPlan(mode=mode))
    with pytest.raises(InjectedFault) as exc:
        injector.hit(mode)
    assert exc.value.mode == mode

def test_fault_trigger_can_be_bounded():
    injector = FaultInjector(FaultPlan(FaultMode.LLM_TIMEOUT, trigger_count=1))
    with pytest.raises(InjectedFault):
        injector.hit(FaultMode.LLM_TIMEOUT)
    injector.hit(FaultMode.LLM_TIMEOUT)
