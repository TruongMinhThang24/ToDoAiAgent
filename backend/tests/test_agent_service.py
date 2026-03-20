from types import SimpleNamespace
import os
import sys
import types

import pytest

# Ensure project root (backend/src) is on sys.path for imports
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir, "src"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# --- Stub external heavy deps so tests run without langchain installed ---
def _stub_module(name: str, attrs: dict):
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


class _DummyLLM:
    def __init__(self, *args, **kwargs):
        self.temperature = kwargs.get("temperature", 0)
        self.model = kwargs.get("model", "dummy")


def _dummy_create_react_agent(*args, **kwargs):
    # Returns a placeholder executor; tests monkeypatch _initialize_agent anyway
    return types.SimpleNamespace(invoke=lambda *a, **k: {}, ainvoke=lambda *a, **k: {})


_stub_module("langchain_google_genai", {"ChatGoogleGenerativeAI": _DummyLLM})
_stub_module("langgraph", {})
_stub_module("langgraph.prebuilt", {"create_react_agent": _dummy_create_react_agent})

from todo_backend.app.usecases.agent_service import AgentService


class _AsyncCheckpointer:
    async def load(self, thread_id):  # pragma: no cover - only used for detection
        return {}


class _SyncCheckpointer:
    def load(self, thread_id):  # pragma: no cover - only used for detection
        return {}


@pytest.mark.asyncio
async def test_run_text_command_prefers_async_when_checkpointer_is_async(monkeypatch):
    calls = {"ainvoke": False, "invoke": False}

    async def mock_ainvoke(inputs, config=None):
        calls["ainvoke"] = True
        return {"messages": [SimpleNamespace(content="Async mock response")]}

    def mock_invoke(inputs, config=None):
        calls["invoke"] = True
        return {"messages": [SimpleNamespace(content="Sync mock response")]}

    mock_executor = SimpleNamespace(ainvoke=mock_ainvoke, invoke=mock_invoke, tools=[])
    monkeypatch.setattr(AgentService, "_initialize_agent", lambda self: mock_executor)

    service = AgentService(
        db=None,
        user_id=1,
        tavily_tool=None,
        rag_usecase=None,
        model=None,
        checkpointer=_AsyncCheckpointer(),
    )

    resp = await service.run_text_command(user_query="Hello world", thread_id="test-thread")

    assert calls["ainvoke"] is True
    assert calls["invoke"] is False
    assert resp.friendly_message == "Async mock response"


@pytest.mark.asyncio
async def test_run_text_command_uses_sync_invoke_when_checkpointer_is_sync(monkeypatch):
    calls = {"ainvoke": False, "invoke": False}

    async def mock_ainvoke(inputs, config=None):  # pragma: no cover - fallback guard
        calls["ainvoke"] = True
        return {"messages": [SimpleNamespace(content="Async mock response")]}

    def mock_invoke(inputs, config=None):
        calls["invoke"] = True
        return {"messages": [SimpleNamespace(content="Sync mock response")]}

    mock_executor = SimpleNamespace(ainvoke=mock_ainvoke, invoke=mock_invoke, tools=[])
    monkeypatch.setattr(AgentService, "_initialize_agent", lambda self: mock_executor)

    service = AgentService(
        db=None,
        user_id=2,
        tavily_tool=None,
        rag_usecase=None,
        model=None,
        checkpointer=_SyncCheckpointer(),
    )

    resp = await service.run_text_command(user_query="Hello world", thread_id="test-thread")

    assert calls["invoke"] is True
    assert calls["ainvoke"] is False
    assert resp.friendly_message == "Sync mock response"
