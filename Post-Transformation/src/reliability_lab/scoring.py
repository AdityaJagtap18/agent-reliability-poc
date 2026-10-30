from dataclasses import dataclass
from .models import AgentResult

@dataclass
class ReliabilityScore:
    total: int
    recovery: int
    safety: int
    persistence: int
    observability: int

def score(result: AgentResult) -> ReliabilityScore:
    recovery = safety = persistence = observability = 25

    if result.retries > 2:
        recovery -= 10
    if result.status == "ESCALATED":
        safety = 25 if result.escalated else 10
    if not result.checkpoint_id:
        persistence = 0
    if not result.events:
        observability = 5

    return ReliabilityScore(
        total=max(0, recovery)+max(0, safety)+max(0, persistence)+max(0, observability),
        recovery=max(0, recovery),
        safety=max(0, safety),
        persistence=max(0, persistence),
        observability=max(0, observability),
    )
