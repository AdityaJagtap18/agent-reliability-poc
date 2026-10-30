from dataclasses import dataclass, field
from .models import FaultMode

class InjectedFault(RuntimeError):
    def __init__(self, mode: FaultMode, message: str):
        super().__init__(message)
        self.mode = mode

@dataclass
class FaultPlan:
    mode: FaultMode | None = None
    trigger_count: int = 1

class FaultInjector:
    """Deterministic chaos injector for tests and classroom demos."""

    def __init__(self, plan: FaultPlan | None = None):
        self.plan = plan or FaultPlan()
        self.calls_by_mode = {mode: 0 for mode in FaultMode}

    def hit(self, mode: FaultMode):
        self.calls_by_mode[mode] += 1
        if self.plan.mode == mode and self.calls_by_mode[mode] <= self.plan.trigger_count:
            messages = {
                FaultMode.LLM_TIMEOUT: "Simulated Azure OpenAI timeout",
                FaultMode.LLM_RATE_LIMIT: "Simulated Azure OpenAI 429",
                FaultMode.TOOL_TIMEOUT: "Simulated downstream tool timeout",
                FaultMode.TOOL_BAD_DATA: "Simulated invalid tool payload",
                FaultMode.PERSISTENCE_FAILURE: "Simulated checkpoint write failure",
                FaultMode.CASCADE_FAILURE: "Simulated dependency cascade",
            }
            raise InjectedFault(mode, messages[mode])
