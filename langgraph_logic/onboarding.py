from langchain.schema import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph_logic.models import *
from enum import Enum

"""
| Field                          | Example                                                                                           |
| ------------------------------ | ------------------------------------------------------------------------------------------------- |
| Full name                      | “Alex Morgan”                                                                                     |
| Tagline / One-liner            | “AI engineer building intelligent automation systems”                                             |
| Bio                            | 2–3 sentence summary (“I’m a software developer interested in agent frameworks and LLM tooling.”) |
| Location / timezone (optional) | “Berlin, Germany”                                                                                 |

"""

class Step(Enum):
    ASK_NAME = "ask_name"
    VERIFY_NAME = "verify_name"

def onboarding_agent(state: AgentState):
    """Initial entry point for the Onboarding Agent, it will determine the next step to display to the user"""
    current_step = state.get("current_step", "")
    is_valid_step = current_step in [s.value for s in Step]

    if not is_valid_step:
        return {
            "current_step": "invalid_step",
            "messages": state["messages"]
        }
    
    return {
        "current_step": current_step,
        "messages": state["messages"]
    }

def ask_name(state: AgentState):
    """Asks the user for their full name"""
    next_step = Step.VERIFY_NAME.value
    return {
        "current_step": next_step,
        "messages": state["messages"] + [AIMessage(content="What is your name?")],
    }

def verify_name(state: AgentState):
    """Validates the user's full name before proceeding to the next step"""
    next_step = Step.VERIFY_NAME.value
    return {
        "current_step": next_step,
        "messages": state["messages"] + [AIMessage(content="Thanks! Your name has been recorded.")],
    }

def invalid_step(state: AgentState):
    return {
        "messages": state["messages"] + [
            AIMessage(content=f"⚠️ Invalid step `{state.get('current_step')}`")
        ],
        "current_agent":"",
        "current_step": "",
    }

def build_onboarding_graph():
    graph = StateGraph(AgentState)

    graph.add_node(onboarding_agent)
    graph.add_node(ask_name)
    graph.add_node(verify_name)
    graph.add_node(invalid_step)

    graph.add_edge(START, "onboarding_agent")

    # Route based on current_step (resume logic)
    graph.add_conditional_edges(
        "onboarding_agent",
        lambda state: state["current_step"],
        {
            Step.ASK_NAME.value: "ask_name",
            Step.VERIFY_NAME.value: "verify_name",
            "invalid_step": "invalid_step",
        },
    )

    # Each step just ends (I'll re-invoke later)
    graph.add_edge("ask_name", END)
    graph.add_edge("verify_name", END)
    graph.add_edge("invalid_step", END)

    return graph.compile()


if __name__ == "__main__":
    from pprint import pprint
    graph = build_onboarding_graph()
    graph.update_state
    new_chat: AgentState = {"current_step": "ask_name","current_agent":"","messages": [HumanMessage(content="github")]}
    result = graph.invoke(new_chat)
    pprint(result, indent=2)