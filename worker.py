"""Temporal Worker - Executes workflows and activities."""

import asyncio
import os
from datetime import timedelta

from dotenv import load_dotenv
from temporalio.client import Client
from temporalio.contrib.openai_agents import (
    LitellmProvider,
    ModelActivityParameters,
    OpenAIAgentsPlugin,
)
from temporalio.worker import Worker

from activities.activities import mcp_search_activity
from workflows.workflow import QnAWorkflow

load_dotenv()

ADDRESS = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "agent-mcp-queue")


async def main() -> None:
    """Initialize and run the Temporal worker."""
    plugin = OpenAIAgentsPlugin(
        model_params=ModelActivityParameters(
            start_to_close_timeout=timedelta(seconds=30)
        ),
        model_provider=LitellmProvider(),
    )

    client = await Client.connect(
        ADDRESS,
        namespace=NAMESPACE,
        plugins=[plugin],
    )
    
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[QnAWorkflow],
        activities=[mcp_search_activity],
    )
    
    print(f"🚀 Worker started. Task queue: {TASK_QUEUE}")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())