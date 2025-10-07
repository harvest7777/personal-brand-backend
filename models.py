from langgraph.graph import MessagesState
from typing import Optional

class AgentState(MessagesState):
    current_agent: str
    current_step: int
