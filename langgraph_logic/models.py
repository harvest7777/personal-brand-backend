from langgraph.graph import MessagesState

class AgentState(MessagesState):
    asi_one_id: str
    current_agent: str
    current_step: str 


