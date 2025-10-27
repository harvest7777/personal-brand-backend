from uagents_core.contrib.protocols.chat import ChatMessage, MetadataContent, TextContent
from langchain_core.messages import HumanMessage
from langgraph_logic.models import AgentState

def initialize_agent_state(asi_one_id: str) -> AgentState:
    """Initializes a new blank AgentState"""
    new_chat: AgentState = {
        "asi_one_id": asi_one_id,
        "current_step": "",
        "current_agent": "",
        "messages": []
    }
    return new_chat

def append_message_to_state(state: AgentState, text: str) -> AgentState:
    state["messages"].append(HumanMessage(content=text))
    return state