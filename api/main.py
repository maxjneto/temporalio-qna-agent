from datetime import timedelta
import os
import sys
import uuid
from pathlib import Path
from typing import Optional

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from temporalio.client import Client
from temporalio.exceptions import WorkflowAlreadyStartedError
from temporalio.service import RPCError, RPCStatusCode

# Add the project root to sys.path so that the "workflows" package is recognized
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import workflow definitions/types
from workflows.workflow import QnAInput, QnAWorkflow

TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
TASK_QUEUE = os.getenv("TASK_QUEUE", "agent-mcp-queue")

@asynccontextmanager
async def lifespan(app: FastAPI):
    from temporalio.contrib.openai_agents import OpenAIAgentsPlugin, ModelActivityParameters
    app.state.temporal_client = await Client.connect(
        TEMPORAL_ADDRESS,
        plugins=[
            OpenAIAgentsPlugin(
                model_params=ModelActivityParameters(
                    start_to_close_timeout=timedelta(seconds=30)
                )
            ),
        ],
    )
    try:
        yield
    finally:
        pass

app = FastAPI(title="Temporal QnA API", lifespan=lifespan)


class StartRequest(BaseModel):
    workflow_id: Optional[str] = None


class PromptRequest(BaseModel):
    prompt: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/workflows", summary="List running workflow IDs")
async def list_running_workflows(workflow_type: Optional[str] = Query(default="QnAWorkflow")):
    client: Client = app.state.temporal_client
    query_parts = ["ExecutionStatus = 'Running'"]
    if workflow_type:
        query_parts.append(f"WorkflowType = '{workflow_type}'")
    query = " and ".join(query_parts)

    ids: list[str] = []
    try:
        async for wf in client.list_workflows(query):
            wf_id = getattr(wf, "id", None) or getattr(getattr(wf, "execution", None), "id", None)
            if wf_id:
                ids.append(wf_id)
    except RPCError as e:
        raise HTTPException(status_code=500, detail=f"Temporal visibility query failed: {e}")

    return {"query": query, "workflow_ids": ids}

@app.post("/workflows/start")
async def start_workflow(req: StartRequest):
    client: Client = app.state.temporal_client
    workflow_id = req.workflow_id or f"qna-workflow-{uuid.uuid4()}"

    try:
        handle = await client.start_workflow(
            QnAWorkflow.run,
            id=workflow_id,
            task_queue=TASK_QUEUE,
        )
    except WorkflowAlreadyStartedError:
        handle = client.get_workflow_handle(workflow_id)

    return {"workflow_id": handle.id, "run_id": handle.run_id}


@app.post("/workflows/{workflow_id}/prompt")
async def send_prompt(workflow_id: str, req: PromptRequest):
    client: Client = app.state.temporal_client
    handle = client.get_workflow_handle(workflow_id)
    try:
        await handle.signal("new_task", QnAInput(query=req.prompt, top_k=3))
    except RPCError as e:
        if e.status == RPCStatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail=str(e))
        raise
    return {"status": "prompt_sent", "workflow_id": workflow_id}


@app.get("/workflows/{workflow_id}/status")
async def get_status(workflow_id: str):
    client: Client = app.state.temporal_client
    handle = client.get_workflow_handle(workflow_id)
    try:
        latest = await handle.query("get_latest_process_info")
    except RPCError as e:
        if e.status == RPCStatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail=str(e))
        raise
    except Exception:
        latest = None
    return {"workflow_id": workflow_id, "latest": latest}


@app.post("/workflows/{workflow_id}/end")
async def end_workflow(workflow_id: str):
    client: Client = app.state.temporal_client
    handle = client.get_workflow_handle(workflow_id)
    try:
        await handle.signal("end_chat")
    except RPCError as e:
        if e.status == RPCStatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail=str(e))
        raise
    return {"status": "ended", "workflow_id": workflow_id}


@app.get("/workflows/{workflow_id}/history")
async def get_history(workflow_id: str):
    client: Client = app.state.temporal_client
    handle = client.get_workflow_handle(workflow_id)
    try:
        history = await handle.query("get_conversation_history")
    except RPCError as e:
        if e.status == RPCStatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail=str(e))
        raise
    return {"workflow_id": workflow_id, "history": history}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=False)
