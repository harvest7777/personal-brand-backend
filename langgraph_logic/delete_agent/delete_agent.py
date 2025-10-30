from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph_logic.models import *
from langgraph_logic.agents import Agent
from langgraph_logic.delete_agent.delete_types import Step
from langgraph_logic.delete_agent.delete_helpers import is_valid_delete_request, is_affirmative_response

def delete_agent(state: AgentState):
    """Initial entry point for the Delete Agent, it will determine the next step to display to the user"""
    current_step = state.get("current_step")
    is_valid_step = current_step in [s.value for s in Step]
    print(f"Current step: {current_step}")

    if not current_step or not is_valid_step:
        # We could check what information we already have about the user at this point then route them properly
        # inferred_step = get_current_step(get_milestone_step_statuses(state["asi_one_id"]))
        # current_step = inferred_step.value
        current_step = Step.DESCRIBE_DATA_TO_DELETE.value

    return {
        "current_step": current_step,
        "messages": state["messages"]
    }

def describe_data_to_delete(state: AgentState):
    """Describe the data to delete"""
    return {
        "current_step": Step.CONFIRM_DELETE.value,
        "current_agent": Agent.DELETE.value,
        "messages": state["messages"] + [AIMessage(content=f"Please describe the data you want to delete. Example: 'I want to delete my work experience at Walmart'")]
    }

def confirm_delete(state: AgentState):
    """Select the data to delete"""

    # Get the described data to delete
    user_input = state["messages"][-1].content
    print(f"User input: {user_input}")


    if not user_input or not is_valid_delete_request(user_input): # type: ignore
        return {
            "current_step": Step.DESCRIBE_DATA_TO_DELETE.value,
            "current_agent": Agent.DELETE.value,
            "messages": state["messages"] + [AIMessage(content=f"That doesn't seem right... Please describe the data you want to delete.")]
        }

    # to_delete = to_delete_from_user_input(user_input)
    to_delete = "WILL QUERY DB FOR DATA TO DELETE LATER"

    return {
        "current_step": Step.COMPLETE.value,
        "current_agent": Agent.DELETE.value,
        "messages": state["messages"] + [AIMessage(content=f"The following data will be deleted: {to_delete}\n\nAre you sure?")]
    }

def complete(state: AgentState):
    """The deletion process has been completed"""

    user_input = state["messages"][-1].content

    if not is_affirmative_response(user_input): # type: ignore
        return {
            "current_step": "",
            "current_agent": "",
            "messages": state["messages"] + [AIMessage(content=f"The deletion process has been aborted.")]
        }

    return {
        "current_step": "",
        "current_agent": "",
        "messages": state["messages"] + [AIMessage(content=f"The deletion process has been completed.")]
    }

def build_delete_graph():
    graph = StateGraph(AgentState)

    graph.add_node(delete_agent)
    for step in Step:
        graph.add_node(globals()[step.value])

    graph.add_edge(START, "delete_agent")

    graph.add_conditional_edges(
        "delete_agent",
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
    graph = build_delete_graph()
    new_chat: AgentState = {"asi_one_id": "user123", "current_step": "", "current_agent": "", "messages": [HumanMessage(content="delete")]}
    result = graph.invoke(new_chat)
    pprint(result, indent=2)

