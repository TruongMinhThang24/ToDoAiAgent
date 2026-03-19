import asyncio
from types import SimpleNamespace
import pytest

from todo_backend.app.usecases.agent_service import AgentService

@pytest.mark.asyncio
async def test_run_text_command_with_mocked_agent_executor():
    # Prepare a mocked async agent executor
    async def mock_ainvoke(inputs, config=None):
        return {"messages": [SimpleNamespace(content="Mock agent response")]} 

    mock_executor = SimpleNamespace(ainvoke=mock_ainvoke, tools=[])

    # Patch the _initialize_agent method before instantiation
    original_init = AgentService._initialize_agent
    AgentService._initialize_agent = lambda self: mock_executor

    try:
        service = AgentService(db=None, user_id=1, tavily_tool=None, rag_usecase=None, model=None, checkpointer=None)
        resp = await service.run_text_command(user_query="Hello world", thread_id="test-thread")
        assert resp is not None
        assert "Mock agent response" in resp.friendly_message
    finally:
        # restore
        AgentService._initialize_agent = original_init
