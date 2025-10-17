from langgraph.graph import StateGraph, START, END
from langchain.schema import HumanMessage, AIMessage
from langgraph_logic.models import *
from langgraph_logic.github import build_github_graph
from pprint import pprint
from langgraph_logic.agents import *

# --- Intent Router ---
def intent_router(state: AgentState):
    # Continuing where we left off, user is already working with an agent and is in some step
    if "current_agent" in state and state["current_agent"] in [agent.value for agent in Agent]:
        return {"next": state["current_agent"]}

    # New conversation or the user has exited one of the other agents 
    # next_node = classify_intent(state)
    return {"next": Agent.FALLBACK.value}


# --- Mock Agents ---
# Each agent has steps?
def linkedin_agent(state: AgentState):
    return {"messages": [AIMessage(content="Opening LinkedIn profile...")]}

def resume_agent(state: AgentState):
    return {"messages": [AIMessage(content="Ready to upload your resume.")]}

def fallback_agent(state: AgentState):
    default_message = """
    [Unclear Intent]
    I am your personal brand assistant. I can help you manage your data, connect to your GitHub, LinkedIn, and more.
    """
    return {
        "messages": [AIMessage(content=default_message)],
        "current_agent": "",
        "current_step": 1
    }

# --- Build Graph ---
def build_main_graph():
    graph = StateGraph(AgentState)

    github_agent = build_github_graph()
    graph.add_node(intent_router)
    graph.add_node(linkedin_agent)
    graph.add_node("github_agent", github_agent)
    graph.add_node(resume_agent)
    graph.add_node(fallback_agent)

    graph.add_edge(START, "intent_router")

    graph.add_conditional_edges(
        "intent_router",
        lambda state: state["next"],
        {
            "linkedin_agent": "linkedin_agent",
            "github_agent": "github_agent",
            "resume_agent": "resume_agent",
            "fallback_agent": "fallback_agent",
        },
    )

    for node in ["linkedin_agent", "github_agent", "resume_agent", "fallback_agent"]:
        graph.add_edge(node, END)

    graph = graph.compile()
    return graph


# --- Test ---
if __name__ == "__main__":
    # continue_with_github: AgentState = {"current_step":1,"current_agent":"github_agent","messages": [HumanMessage(content="Post to github for me."), AIMessage(content="Waiting for confirm.")]}
    graph = build_main_graph()
    new_chat: AgentState = {"agent_id":"","current_step":"","current_agent":"","messages": [HumanMessage(content="hi")]}
    result = graph.invoke(new_chat)
    pprint(result, indent=2)
