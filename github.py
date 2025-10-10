from langgraph_models import * 
from langchain.schema import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END

def github_agent(state: AgentState):
    current_step = state.get("current_step", 1)
    
    return {
        "current_step": current_step,
        "messages": state["messages"] + [
            AIMessage(content=f"Resuming at step {current_step}")
        ],
    }

def step1(state: AgentState):
    new_step = state["current_step"] + 1
    return {
        "current_step": new_step,
        "messages": state["messages"] + [AIMessage(content="Executing step 1")],
    }

def step2(state: AgentState):
    new_step = state["current_step"] + 1
    return {
        "current_step": new_step,
        "messages": state["messages"] + [AIMessage(content="Executing step 2")],
    }

def step3(state: AgentState):
    new_step = state["current_step"] + 1
    return {
        "current_step": new_step,
        "messages": state["messages"] + [AIMessage(content="Executing step 3")],
    }

def build_github_graph():
    graph = StateGraph(AgentState)

    graph.add_node(github_agent)
    graph.add_node(step1)
    graph.add_node(step2)
    graph.add_node(step3)

    graph.add_edge(START, "github_agent")

    # Route based on current_step (resume logic)
    graph.add_conditional_edges(
        "github_agent",
        lambda state: state["current_step"],
        {
            1: "step1",
            2: "step2",
            3: "step3",
        },
    )

    # Each step just ends (you'll re-invoke later)
    graph.add_edge("step1", END)
    graph.add_edge("step2", END)
    graph.add_edge("step3", END)

    return graph.compile()
