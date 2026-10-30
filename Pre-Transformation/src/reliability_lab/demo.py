import uuid
from .config import settings
from .agent import ReliabilityAgent
from .models import AgentRequest
from .scoring import score
from .telemetry import configure_logging

def main():
    configure_logging()
    request = AgentRequest(
        request_id=str(uuid.uuid4()),
        customer_id="CUST-1001",
        question="What is the current customer status?",
    )
    result = ReliabilityAgent().run(request)
    print("\n=== Agent Reliability Lab ===")
    print("Mode:", settings.mode)
    print("Status:", result.status)
    print("Answer:", result.answer)
    print("Retries:", result.retries)
    print("Escalated:", result.escalated)
    print("Checkpoint:", result.checkpoint_id)
    print("Reliability score:", score(result).total, "/ 100")

if __name__ == "__main__":
    main()
