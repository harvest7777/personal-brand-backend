from langgraph.graph import StateGraph, START, END
from langchain.schema import HumanMessage, AIMessage
from github import build_github_graph
from models import *
from pprint import pprint


# --- Intent Router ---
def intent_router(state: AgentState):
    if "current_agent" in state and state["current_agent"] is not None:
        return {"next": state["current_agent"]}

    user_msg_obj = state["messages"][-1]
    user_msg_content = str(getattr(user_msg_obj, "content", user_msg_obj))
    user_msg: str = user_msg_content.lower()

    if "linkedin" in user_msg:
        next_node = "linkedin_agent"
    elif "github" in user_msg:
        next_node = "github_agent"
    elif "resume" in user_msg or "upload" in user_msg:
        next_node = "resume_agent"
    else:
        next_node = "fallback_agent"

    return {"next": next_node}

# --- Mock Agents ---


# Each agent has steps?
def linkedin_agent(state: AgentState):
    return {"messages": [AIMessage(content="Opening LinkedIn profile...")]}

def resume_agent(state: AgentState):
    return {"messages": [AIMessage(content="Ready to upload your resume.")]}

def fallback_agent(state: AgentState):
    return {"messages": [AIMessage(content="Sorry, I didn’t understand. Can you clarify?")]}

# --- Build Graph ---
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

# --- Test ---
continue_with_github: AgentState = {"current_step":1,"current_agent":"github_agent","messages": [HumanMessage(content="Post to github for me."), AIMessage(content="Waiting for confirm.")]}
result = graph.invoke(continue_with_github)
pprint(result, indent=2)
