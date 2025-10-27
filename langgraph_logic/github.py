from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph_logic.models import *

VALID_STEPS = [1,2,3]
def github_agent(state: AgentState):
    current_step = state.get("current_step", 1)
    if current_step not in VALID_STEPS:
        return {
            "current_step": "invalid_step",
            "messages": state["messages"] + [
                AIMessage(content=f"Resuming at step {current_step}")
            ],
        }
    
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

def invalid_step(state: AgentState):
    return {
        "messages": state["messages"] + [
            AIMessage(content=f"⚠️ Invalid step `{state.get('current_step')}`")
        ],
        "current_agent":"",
        "current_step": 1,
    }

def build_github_graph():
    graph = StateGraph(AgentState)

    graph.add_node(github_agent)
    graph.add_node(step1)
    graph.add_node(step2)
    graph.add_node(step3)
    graph.add_node(invalid_step)

    graph.add_edge(START, "github_agent")

    # Route based on current_step (resume logic)
    graph.add_conditional_edges(
        "github_agent",
        lambda state: state["current_step"],
        {
            1: "step1",
            2: "step2",
            3: "step3",
            "invalid_step": "invalid_step",
        },
    )

    # Each step just ends (you'll re-invoke later)
    graph.add_edge("step1", END)
    graph.add_edge("step2", END)
    graph.add_edge("step3", END)
    graph.add_edge("invalid_step", END)

    return graph.compile()


if __name__ == "__main__":
    from pprint import pprint
    graph = build_github_graph()
    new_chat: AgentState = {"current_step":1,"current_agent":"","messages": [HumanMessage(content="github")]}
    continue_with_github: AgentState = {"current_step":1,"current_agent":"github_agent","messages": [HumanMessage(content="Post to github for me."), AIMessage(content="Waiting for confirm.")]}
    result = graph.invoke(new_chat)
    pprint(result, indent=2)