from uagents_core.contrib.protocols.chat import ChatMessage, MetadataContent, TextContent
from langchain_core.messages import HumanMessage
from langgraph_agents.models import AgentState

def append_message_to_state(state: AgentState, text: str) -> AgentState:
    state["messages"].append(HumanMessage(content=text))
    return state