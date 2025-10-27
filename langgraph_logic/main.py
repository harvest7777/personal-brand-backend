from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from langgraph_logic.models import *
from langgraph_logic.github import build_github_graph
from pprint import pprint
from langgraph_logic.onboarding import build_onboarding_graph
from langgraph_logic.router_helpers import *
from langgraph_logic.agents import *
from utils.data_serialization_helpers import *
from langgraph_logic.linkedin_agent.linkedin_agent import build_linkedin_graph

# --- Intent Router ---
def intent_router(state: AgentState):
    # Continuing where we left off, user is already working with an agent and is in some step
    if "current_agent" in state and state["current_agent"] in [agent.value for agent in Agent]:
        return {"current_agent": state["current_agent"]}

    # New conversation or the user has exited one of the other agents 
    classified_agent = classify_intent(state)
    print(f"Classified agent: {classified_agent.value}")
    return {"current_agent": classified_agent.value}


# --- Mock Agents ---
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
    onboarding_agent = build_onboarding_graph()
    linkedin_agent = build_linkedin_graph()

    graph.add_node(Agent.GITHUB.value, github_agent)
    graph.add_node(Agent.ONBOARDING.value, onboarding_agent)
    graph.add_node(Agent.LINKEDIN.value, linkedin_agent)

    graph.add_node(intent_router)
    graph.add_node(resume_agent)
    graph.add_node(fallback_agent)

    graph.add_edge(START, "intent_router")

    graph.add_conditional_edges(
        "intent_router",
        lambda state: state["current_agent"],
        {
            Agent.LINKEDIN.value: Agent.LINKEDIN.value,
            Agent.ONBOARDING.value: Agent.ONBOARDING.value,
            Agent.GITHUB.value: Agent.GITHUB.value,
            Agent.RESUME.value: Agent.RESUME.value,
            Agent.FALLBACK.value: Agent.FALLBACK.value,
        },
    )

    for node in [agent.value for agent in Agent]:
        graph.add_edge(node, END)

    graph = graph.compile()
    return graph


# --- Test ---
if __name__ == "__main__":
    graph = build_main_graph()

    new_chat: AgentState = {"asi_one_id":"user1234234","current_step":"","current_agent":"","messages": [HumanMessage(content="i want to connect linkedin")]}
    result = graph.invoke(new_chat)


    pprint(result, indent=2)
