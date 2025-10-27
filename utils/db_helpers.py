from uagents_core.contrib.protocols.chat import ChatMessage, MetadataContent, TextContent
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph_logic.models import AgentState
from utils.data_serialization_helpers import *


def get_most_recent_state_from_agent_db(chat_id: str, ctx) -> AgentState | None:
    """Fetches the most recent AgentState from the agent's db storage.""" 
    chat_data = ctx.storage.get(chat_id)
    if chat_data is None:
        return None
    return json_agent_state_to_langgraph(chat_data)