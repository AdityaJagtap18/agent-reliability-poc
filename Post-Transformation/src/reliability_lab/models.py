from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class FaultMode(str, Enum):
    LLM_TIMEOUT = "llm_timeout"
    LLM_RATE_LIMIT = "llm_rate_limit"
    TOOL_TIMEOUT = "tool_timeout"
    TOOL_BAD_DATA = "tool_bad_data"
    PERSISTENCE_FAILURE = "persistence_failure"
    CASCADE_FAILURE = "cascade_failure"

@dataclass
class AgentRequest:
    request_id: str
    customer_id: str
    question: str

@dataclass
class ToolResult:
    ok: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    source: str = "mock_tool"

@dataclass
class AgentResult:
    request_id: str
    answer: str
    status: str
    retries: int
    escalated: bool
    degraded: bool
    checkpoint_id: str | None = None
    events: list[dict[str, Any]] = field(default_factory=list)
