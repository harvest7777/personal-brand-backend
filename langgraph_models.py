from langgraph.graph import MessagesState

class AgentState(MessagesState):
    current_agent: str
    current_step: int



