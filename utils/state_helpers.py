from uagents_core.contrib.protocols.chat import ChatMessage, MetadataContent, TextContent
from langchain.schema import HumanMessage
from langgraph_logic.models import AgentState

def initialize_agent_state() -> AgentState:
    """Initializes a new blank AgentState"""
    new_chat: AgentState = {"current_step":1,"current_agent":"","messages": []}
    return new_chat

def append_message_to_state(state: AgentState, text: str) -> AgentState:
    state["messages"].append(HumanMessage(content=text))
    return state