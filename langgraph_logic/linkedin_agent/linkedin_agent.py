from langchain.schema import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph_logic.composio_client import *
from supabase_auth import UserResponse
from chroma.chroma_helpers import insert_resume_fact
from langgraph_logic.models import *
from enum import Enum
from langgraph_logic.onboarding_helpers import *

def linkedin_agent(state: AgentState):
    """Initial entry point for the LinkedIn Agent, it will determine the next step to display to the user"""


    return {
        "current_step": "",
        "messages": state["messages"]
    }



def build_linkedin_graph():
    graph = StateGraph(AgentState)

    graph.add_node(linkedin_agent)

    graph.add_edge(START, "linkedin_agent")
    graph.add_edge("linkedin_agent", END)



    return graph.compile()


if __name__ == "__main__":
    from pprint import pprint
    graph = build_linkedin_graph()
    new_chat: AgentState = {"agent_id": "user123", "current_step": "", "current_agent": "", "messages": [HumanMessage(content="github")]}
    result = graph.invoke(new_chat)
    pprint(result, indent=2)

