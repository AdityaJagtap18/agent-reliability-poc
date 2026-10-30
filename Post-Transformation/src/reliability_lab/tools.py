from .faults import FaultInjector
from .models import FaultMode, ToolResult

class CustomerTool:
    """Deterministic simulated enterprise tool."""

    def __init__(self, faults=None):
        self.faults = faults or FaultInjector()

    def get_customer_status(self, customer_id: str) -> ToolResult:
        self.faults.hit(FaultMode.TOOL_TIMEOUT)
        self.faults.hit(FaultMode.CASCADE_FAILURE)
        return ToolResult(
            ok=True,
            data={
                "customer_id": customer_id,
                "tier": "gold",
                "open_cases": 2,
                "credit_limit": 50000,
            },
        )

    def get_customer_status_untrusted(self, customer_id: str) -> ToolResult:
        self.faults.hit(FaultMode.TOOL_BAD_DATA)
        return ToolResult(
            ok=True,
            data={
                "customer_id": customer_id,
                "tier": "gold",
                "open_cases": "two",
                "credit_limit": -50000,
            },
        )
