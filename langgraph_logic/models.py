from langgraph.graph import MessagesState
from pydantic import BaseModel
from langchain_core.messages import AnyMessage


class GatherAgentState(BaseModel):
    current_topic: str
    current_question: str

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)



class DeleteAgentState(BaseModel):
    data_ids_to_delete: list[str]
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class AgentState(BaseModel):
    asi_one_id: str
    current_agent: str
    current_step: str 
    gather_agent_state: GatherAgentState 
    delete_agent_state: DeleteAgentState
    messages: list[AnyMessage]
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def to_json(self) -> dict:
        return {
            "asi_one_id": self.asi_one_id,
            "current_agent": self.current_agent,
            "current_step": self.current_step,
            "gather_agent_state": (
                self.gather_agent_state.model_dump()
                if hasattr(self.gather_agent_state, "model_dump")
                else self.gather_agent_state.__dict__
            ),
            "delete_agent_state": (
                self.delete_agent_state.model_dump()
                if hasattr(self.delete_agent_state, "model_dump")
                else self.delete_agent_state.__dict__
            ),
            "messages": getattr(self, "messages", []),
        }

def initialize_agent_state(asi_one_id: str) -> AgentState:
    return AgentState(
        asi_one_id=asi_one_id,
        current_agent="",
        current_step="",
        gather_agent_state=GatherAgentState(current_topic="", current_question=""),
        delete_agent_state=DeleteAgentState(data_ids_to_delete=[]),
        messages=[]
    )


