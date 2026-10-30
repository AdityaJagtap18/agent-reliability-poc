import uuid
from typing import Any

from .config import settings
from .faults import FaultInjector, InjectedFault
from .models import AgentRequest, AgentResult, FaultMode
from .persistence import LocalCheckpointStore, CosmosCheckpointStore
from .telemetry import emit
from .tools import CustomerTool

class ReliabilityAgent:
    """
    Small agent orchestration layer.

    Python owns reliability policy; Azure OpenAI is used for the final
    natural-language decision when LAB_MODE=azure.
    """

    def __init__(self, faults=None, store=None, use_azure=None):
        self.faults = faults or FaultInjector()
        self.tool = CustomerTool(self.faults)
        self.store = store or LocalCheckpointStore(faults=self.faults)
        self.use_azure = settings.mode == "azure" if use_azure is None else use_azure

    def _azure_answer(self, question: str, customer: dict[str, Any]) -> str:
        from openai import AzureOpenAI
        client = AzureOpenAI(
            api_key=settings.azure_api_key,
            azure_endpoint=settings.azure_endpoint,
            api_version=settings.azure_api_version,
        )
        response = client.chat.completions.create(
            model=settings.azure_deployment,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a reliability-lab customer support agent. "
                        "Use only supplied customer data. If data is incomplete, "
                        "say so. Never invent a successful operation."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Question: {question}\nCustomer data: {customer}",
                },
            ],
        )
        return response.choices[0].message.content or ""

    def _mock_answer(self, question, customer):
        return (
            f"Customer {customer['customer_id']} is {customer['tier']} tier "
            f"with {customer['open_cases']} open cases."
        )

    def _answer(self, question, customer):
        self.faults.hit(FaultMode.LLM_TIMEOUT)
        self.faults.hit(FaultMode.LLM_RATE_LIMIT)
        return self._azure_answer(question, customer) if self.use_azure else self._mock_answer(question, customer)

    def run(self, request: AgentRequest) -> AgentResult:
        checkpoint_id = f"cp-{request.request_id}-{uuid.uuid4().hex[:8]}"
        events, retries = [], 0
        degraded = escalated = False

        try:
            self.store.save(checkpoint_id, {
                "request_id": request.request_id,
                "customer_id": request.customer_id,
                "stage": "STARTED",
                "question": request.question,
            })
            events.append({"event": "checkpoint_saved", "id": checkpoint_id})
        except Exception as exc:
            escalated = True
            events.append({"event": "checkpoint_failed", "error": str(exc)})

        customer = None
        for attempt in range(2):
            try:
                customer = self.tool.get_customer_status(request.customer_id)
                break
            except InjectedFault as exc:
                retries += 1
                events.append({"event": "tool_fault", "mode": exc.mode.value, "attempt": attempt + 1})
                if attempt == 1:
                    degraded = True

        if customer is None:
            return AgentResult(
                request_id=request.request_id,
                answer="I could not safely retrieve customer status. No definitive business action was taken.",
                status="ESCALATED",
                retries=retries,
                escalated=True,
                degraded=degraded,
                checkpoint_id=checkpoint_id,
                events=events,
            )

        data = customer.data
        if not isinstance(data.get("open_cases"), int) or data.get("credit_limit", 0) < 0:
            return AgentResult(
                request_id=request.request_id,
                answer="The downstream system returned invalid customer data. I will not use it for a business decision.",
                status="ESCALATED",
                retries=retries,
                escalated=True,
                degraded=True,
                checkpoint_id=checkpoint_id,
                events=events,
            )

        answer = None
        for attempt in range(2):
            try:
                answer = self._answer(request.question, data)
                break
            except InjectedFault as exc:
                retries += 1
                events.append({"event": "llm_fault", "mode": exc.mode.value, "attempt": attempt + 1})
                if attempt == 1:
                    degraded = True

        if answer is None:
            answer = "The reasoning service is temporarily unavailable. I will not provide a definitive answer."
            status = "DEGRADED"
            escalated = True
        else:
            status = "DEGRADED" if degraded else "SUCCESS"

        try:
            self.store.save(checkpoint_id, {
                "request_id": request.request_id,
                "customer_id": request.customer_id,
                "stage": "COMPLETED",
                "status": status,
                "answer": answer,
                "retries": retries,
            })
        except Exception as exc:
            escalated = True
            events.append({"event": "completion_checkpoint_failed", "error": str(exc)})

        emit("agent.run",
             request_id=request.request_id,
             status=status,
             retries=retries,
             degraded=degraded,
             escalated=escalated)

        return AgentResult(
            request_id=request.request_id,
            answer=answer,
            status=status,
            retries=retries,
            escalated=escalated,
            degraded=degraded,
            checkpoint_id=checkpoint_id,
            events=events,
        )

def build_store():
    if settings.mode == "azure":
        return CosmosCheckpointStore(
            settings.cosmos_endpoint,
            settings.cosmos_key,
            settings.cosmos_database,
            settings.cosmos_container,
        )
    return LocalCheckpointStore()
