from langgraph_logic.models import *
from langchain.schema import HumanMessage, AIMessage
from langchain_core.messages import AnyMessage
from database.agent_db_models import *

def jsonAgentStateToLangGraph(json_data) -> AgentState:
    current_agent: str = json_data.current_agent
    current_step: int = json_data.current_step
    messages: List[AnyMessage] = []

    for msg in json_data.messages:
        match msg.role:
            case "human":
                messages.append(HumanMessage(content=msg.content))
            case "ai":
                messages.append(AIMessage(content=msg.content))
            case _:
                raise ValueError(f"Unknown role: {msg.role}")

    langgraph_agent_state = AgentState(
        current_agent=current_agent,
        current_step=current_step,
        messages=messages
    )
    return langgraph_agent_state
