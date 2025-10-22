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

    asi_one_id = state["asi_one_id"]
    connection_request = composio.connected_accounts.link(asi_one_id, LINKEDIN_AUTH_CONFIG_ID)

    redirect_url = connection_request.redirect_url
    return {
        "current_step": "",
        "current_agent": "",
        "messages": state["messages"] + [AIMessage(content=f"Please [click here to connect your LinkedIn account]({redirect_url}).")]
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
    new_chat: AgentState = {"asi_one_id": "user123", "current_step": "", "current_agent": "", "messages": [HumanMessage(content="github")]}
    result = graph.invoke(new_chat)
    pprint(result, indent=2)

