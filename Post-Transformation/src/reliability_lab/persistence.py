import json
from pathlib import Path
from typing import Any
from .faults import FaultInjector
from .models import FaultMode

class LocalCheckpointStore:
    """Local durable adapter used for offline demos and pytest."""

    def __init__(self, path="local_state/checkpoints.json", faults=None):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.faults = faults or FaultInjector()

    def _read(self):
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text())

    def save(self, checkpoint_id: str, state: dict[str, Any]):
        self.faults.hit(FaultMode.PERSISTENCE_FAILURE)
        data = self._read()
        data[checkpoint_id] = state
        self.path.write_text(json.dumps(data, indent=2, default=str))
        return checkpoint_id

    def load(self, checkpoint_id: str):
        return self._read().get(checkpoint_id)

class CosmosCheckpointStore:
    """Azure Cosmos DB NoSQL persistence adapter."""

    def __init__(self, endpoint, key, database, container, faults=None):
        from azure.cosmos import CosmosClient, PartitionKey
        self.faults = faults or FaultInjector()
        self.client = CosmosClient(endpoint, key)
        self.database = self.client.create_database_if_not_exists(id=database)
        self.container = self.database.create_container_if_not_exists(
            id=container,
            partition_key=PartitionKey(path="/partitionKey"),
        )

    def save(self, checkpoint_id, state):
        self.faults.hit(FaultMode.PERSISTENCE_FAILURE)
        item = {
            "id": checkpoint_id,
            "partitionKey": state.get("request_id", checkpoint_id),
            **state,
        }
        self.container.upsert_item(item)
        return checkpoint_id

    def load(self, checkpoint_id):
        query = "SELECT * FROM c WHERE c.id = @id"
        rows = list(self.container.query_items(
            query=query,
            parameters=[{"name": "@id", "value": checkpoint_id}],
            enable_cross_partition_query=True,
        ))
        return rows[0] if rows else None
