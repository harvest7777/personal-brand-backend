from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph_logic.models import *
from langgraph_logic.agents import Agent
from langgraph_logic.gather_agent.gather_steps import Step
from langgraph_logic.delete_agent.delete_helpers import is_valid_delete_request, is_affirmative_response

def gather_agent(state: AgentState):
    """Initial entry point for the Delete Agent, it will determine the next step to display to the user"""
    current_step = state.get("current_step")
    is_valid_step = current_step in [s.value for s in Step]
    print(f"Current step: {current_step}")

    if not current_step or not is_valid_step:
        # We could check what information we already have about the user at this point then route them properly
        # inferred_step = get_current_step(get_milestone_step_statuses(state["asi_one_id"]))
        # current_step = inferred_step.value
        current_step = Step.ASK_QUESTION.value

    return {
        "current_step": current_step,
        "messages": state["messages"]
    }

def build_gather_graph():
    graph = StateGraph(AgentState)

    graph.add_node(gather_agent)
    for step in Step:
        graph.add_node(globals()[step.value])

    graph.add_edge(START, "gather_agent")

    graph.add_conditional_edges(
        "gather_agent",
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
    graph = build_gather_graph()
    new_chat: AgentState = {"asi_one_id": "user123", "current_step": "", "current_agent": "", "messages": [HumanMessage(content="delete")]}
    result = graph.invoke(new_chat)
    pprint(result, indent=2)

