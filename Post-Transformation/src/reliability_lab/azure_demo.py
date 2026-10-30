from .config import settings
from .agent import ReliabilityAgent, build_store
from .models import AgentRequest
from .scoring import score

def main():
    if settings.mode != "azure":
        raise SystemExit("Set LAB_MODE=azure in .env first.")
    result = ReliabilityAgent(
        store=build_store(),
        use_azure=True,
    ).run(
        AgentRequest(
            request_id="azure-demo-001",
            customer_id="CUST-1001",
            question="Summarize this customer's operational status.",
        )
    )
    print("\n=== Azure OpenAI + Cosmos DB Demo ===")
    print(result.answer)
    print("status:", result.status)
    print("checkpoint:", result.checkpoint_id)
    print("score:", score(result).total, "/ 100")

if __name__ == "__main__":
    main()
