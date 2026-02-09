"""Temporal Workflows - Q&A workflow with agents."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Deque

from agents import Agent, Runner
from temporalio import workflow
from temporalio.contrib import openai_agents

from activities.activities import mcp_search_activity

@dataclass
class QnAInput:
    query: str
    top_k: int = 3

from collections import deque
from datetime import timedelta
from typing import Any, Deque, Dict, List, Optional, TypedDict, Union

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.contrib import openai_agents

@workflow.defn
class QnAWorkflow:
    """Workflow that manages tool execution with user confirmation and conversation history."""

    def __init__(self) -> None:
        self.conversation_history = []
        self.prompt_queue: Deque[QnAInput] = deque()
        self.current_prompt: QnAInput = None
        self.chat_ended = False
        self.current_state = []

        self.system_prompt = (
            "You are an assistant specialized in synthesis. "
            "To have a better context to answer a user question about software development/programming, use the 'mcp_search_activity' tool to search for relevant documents. "
            "Respond only based on the CONTEXT returned by it, citing excerpts using [n] when relevant."
            "If no external information is needed, just say so."
        )

    # see ../api/main.py#temporal_client.start_workflow() for how the input parameters are set
    @workflow.run
    async def run(self) -> str:

        agent = Agent(
            name="QnA Agent",
            model="azure/gpt-4o",
            instructions=self.system_prompt,
            tools=[
                openai_agents.workflow.activity_as_tool(
                    mcp_search_activity,
                    start_to_close_timeout=timedelta(seconds=60)
                )
            ],
        )
        while True:
            await workflow.wait_condition(
                lambda: bool(self.prompt_queue) or self.chat_ended
            )

            if self.chat_ended:
                break

            if self.prompt_queue:
                task = self.prompt_queue.popleft()
                workflow.logger.info(
                    f"workflow step: processing message on the prompt queue, message is {task.query}"
                )

                self.add_message("user", task.query)

                self.current_state.clear()

                self.current_state.append({
                    "content": task.query,
                    "state": "prompt"
                })

                result = await Runner.run(starting_agent=agent,input=task.query)
                answer = result.final_output

                self.add_message("agent", answer)

                break

        return str(self.conversation_history)

    @workflow.signal
    async def new_task(self, task: QnAInput) -> None:
        """Signal handler for receiving user prompts."""
        workflow.logger.info(f"signal received: user_prompt, prompt is {task.query}")
        if self.chat_ended:
            workflow.logger.info(f"Message dropped due to chat closed: {task.query}")
            return
        self.prompt_queue.append(task)

    # Signal that comes from api/main.py via a post to /end-chat
    @workflow.signal
    async def end_chat(self) -> None:
        """Signal handler for ending the chat session."""
        workflow.logger.info("signal received: end_chat")
        self.chat_ended = True

    @workflow.query
    def get_conversation_history(self):
        """Query handler to retrieve the full conversation history."""
        return self.conversation_history

    @workflow.query
    def get_latest_process_info(self):
        latest = self.conversation_history[-1] if self.conversation_history else None
        return {"latest_message": latest, "current_state": self.current_state}

    def add_message(self, actor: str, message: str) -> None:
        workflow.logger.debug(f"Adding {actor} message: {message[:100]}...")

        self.conversation_history.append(
            {"actor": actor, "content": message}
        )

    def construct_prompt(self, documents: list[dict], user_prompt: str) -> str:
        """Constructs prompt with context from found documents.
        
        Args:
            documents: List of relevant documents
            user_prompt: Original user question
            
        Returns:
            Formatted prompt with context and instructions
        """
        context_text = ""
        for doc in documents:
            context_text += f'[{doc["id"]}] - {doc["chunk"]}\n'

        prompt = (
            f"User question: {user_prompt}\n\n"
            f"=== CONTEXT ===\n{context_text}\n"
            f"=== INSTRUCTION ===\n"
            f"Produce a concise answer, citing excerpts using [n] when relevant."
        )

        return prompt