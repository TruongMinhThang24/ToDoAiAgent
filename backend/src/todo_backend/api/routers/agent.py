from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
import uuid
import logging

from ..schemas.chat_schema import AgentExecuteRequest, AgentChatReponse
from ..routers.chat import agent_service_dependency, user_dependency

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/agent", tags=["Agent"])

@router.post("/execute", response_model=AgentChatReponse)
async def execute_agent(
    request: AgentExecuteRequest,
    user: Annotated[dict, Depends(user_dependency)],
    agent_service = Depends(agent_service_dependency),
):
    owner_id = user["id"]
    # Build/validate thread id
    new_uuid = str(uuid.uuid4())
    thread_id = f"user_chat_session_{owner_id}_{new_uuid}"

    try:
        # For now use user_prompt as the text to send to agent
        agent_response = await agent_service.run_text_command(user_query=request.user_prompt, thread_id=thread_id)
        return agent_response
    except Exception as e:
        logger.error(f"Error executing agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Agent execution failed")
