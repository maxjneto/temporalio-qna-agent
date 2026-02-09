"""Standalone Temporal client for testing workflows."""

import asyncio

from temporalio.client import Client

from workflows.workflow import QnAInput


async def main() -> None:
    """Connects to Temporal and sends a task to the workflow."""
    client = await Client.connect("localhost:7233")
    
    # Create workflow input
    input_data = QnAInput(
        query="Tell me some Python libraries for creating APIs.",
        top_k=3
    )
    
    # Start the workflow
    handle = await client.start_workflow(
        "QnAWorkflow",
        id="qna-workflow-002",
        task_queue="agent-mcp-queue",
    )

    # Send task via signal
    await handle.signal("new_task", input_data)
    
    print(f"✅ Task sent to workflow: {handle.id}")

if __name__ == "__main__":
    asyncio.run(main())