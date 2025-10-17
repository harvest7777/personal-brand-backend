from langchain.schema import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from supabase_auth import UserResponse
from langgraph_logic.models import *
from enum import Enum
from langgraph_logic.onboarding_helpers import *

class Step(Enum):
    ASK_NAME = "ask_name"
    VERIFY_NAME = "verify_name"
    ASK_RESUME = "ask_resume"
    INVALID_STEP = "invalid_step"
    STORE_FACTS_FROM_RESUME = "store_facts_from_resume"

def onboarding_agent(state: AgentState):
    """Initial entry point for the Onboarding Agent, it will determine the next step to display to the user"""
    current_step = state.get("current_step")
    is_valid_step = current_step in [s.value for s in Step]

    if not current_step or not is_valid_step:
        # We could check what information we already have about the user at this point then route them properly
        current_step = Step.ASK_NAME.value

    return {
        "current_step": current_step,
        "messages": state["messages"]
    }

def ask_name(state: AgentState):
    """Asks the user for their full name and moves on to the next step"""
    next_step = Step.VERIFY_NAME.value
    return {
        "current_step": next_step,
        "messages": state["messages"] + [AIMessage(content="What is your name?")],
    }

def verify_name(state: AgentState):
    """Validates the user's full name before proceeding to the next step"""
    # Will replace with some llm helper here
    user_response: str = state["messages"][-1].content if state["messages"] else "" # type: ignore

    valid_name = is_valid_name(user_response)

    if not valid_name:
        return {
            "current_step": Step.VERIFY_NAME.value,
            "messages": state["messages"] + [AIMessage(content="That doesn't seem like a valid name. Please try again.")],
        }

    # TODO save this into supabase
    extracted_name = extract_name(user_response)

    # Done with the onboarding flow 
    return {
        "current_step": Step.ASK_RESUME.value,
        "messages": state["messages"] + [AIMessage(content="Thanks! Your name has been recorded. When you're ready to move on to the next step, just send a message!")],
    }

def invalid_step(state: AgentState):
    return {
        "messages": state["messages"] + [
            AIMessage(content=f"⚠️ Invalid step `{state.get('current_step')}`")
        ],
        "current_agent":"",
        "current_step": "",
    }

def ask_resume(state: AgentState):
    """Asks the user for their resume and moves on to the next step"""
    return {
        "current_step": Step.STORE_FACTS_FROM_RESUME.value,
        "messages": state["messages"] + [AIMessage(content="Copy paste your resume so I can start building your profile. No need to worry about formatting, I can take care of it!")],
    }

def store_facts_from_resume(state: AgentState):
    """Asks the user for their resume and moves on to the next step"""

    user_response: str = state["messages"][-1].content if state["messages"] else "" # type: ignore
    facts_from_resume = parse_resume(user_response)

    # TODO store the resume facts in chroma
    return {
        "current_agent":"",
        "current_step": "",
        "messages": state["messages"] + [AIMessage(content="Great, I just parsed your resume to store facts about you.")],
    }


def build_onboarding_graph():
    graph = StateGraph(AgentState)

    # Automatically add all enum step functions as nodes, plus onboarding_agent 
    graph.add_node(onboarding_agent)
    for step in Step:
        graph.add_node(globals()[step.value])

    graph.add_edge(START, "onboarding_agent")

    # Route based on current_step (resume logic)
    graph.add_conditional_edges(
        "onboarding_agent",
        lambda state: state["current_step"],
        {
            **{
                step.value: step.value
                for step in Step
            }
        },
    )

    for node in [step.value for step in Step]:
        graph.add_edge(node, END)

    return graph.compile()


if __name__ == "__main__":
    from pprint import pprint
    graph = build_onboarding_graph()
    new_chat: AgentState = {"agent_id": "user123", "current_step": "", "current_agent": "", "messages": [HumanMessage(content="github")]}
    result = graph.invoke(new_chat)
    pprint(result, indent=2)