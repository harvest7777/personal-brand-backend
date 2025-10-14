from uagents_core.contrib.protocols.chat import ChatMessage, MetadataContent, TextContent
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langchain.schema import HumanMessage
from langgraph_logic.models import AgentState
from utils.data_serialization_helpers import *


def get_most_recent_state_from_agent_db(chat_id: str, ctx) -> AgentState:
    """Fetches the most recent AgentState from the agent's db storage. If none exists, initializes a new one."""
    from utils.state_helpers import initialize_agent_state
    chat_data = ctx.storage.get(chat_id)
    if chat_data is None:
        return initialize_agent_state()
    return json_agent_state_to_langgraph(chat_data)