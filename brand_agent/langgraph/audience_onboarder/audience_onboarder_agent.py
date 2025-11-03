from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.load import dumps, loads
from langgraph.graph import StateGraph, START, END
from brand_agent.brand_agent_helpers import *
from brand_agent.brand_agent_helpers import *
from langgraph_logic.models import *
from brand_agent.langgraph.audience_onboarder.audience_onboarder_steps import Step
from langgraph_logic.models import initialize_agent_state
from langgraph_logic.onboarding_agent.onboarding_helpers import is_valid_name

def audience_onboarder_agent(state: AgentState):
    """Initial entry point for the Audience Onboarder Agent, it will determine the next step to display to the user"""
    current_step = state.get("current_step")
    is_valid_step = current_step in [s.value for s in Step]

    if not current_step or not is_valid_step:
        # Ask name step will be our fallback
        current_step = Step.ASK_NAME.value
    return {
        "current_step": current_step,
        "messages": state["messages"]
    }

def ask_name(state: AgentState):
    """Ask the user for their name"""
    return {
        "current_step": Step.VERIFY_NAME.value,
        "messages": state["messages"] + [AIMessage(content="What is your name?")]
    }

def verify_name(state: AgentState):
    """Verify the user's name"""
    user_input = str(state["messages"][-1].content)
    valid_name = is_valid_name(user_input)
    if not valid_name:
        return {
            "current_step": Step.VERIFY_NAME.value,
            "messages": state["messages"] + [AIMessage(content="That is not a valid name. Please try again.")]
        }

    # TODO db write
    return {
        "current_step": Step.VERIFY_ROLE.value,
        "messages": state["messages"] + [AIMessage(content="That is a valid name. Thank you!\nWhat is your role?")]
    }

def ask_role(state: AgentState):
    """Ask the user for their role"""
    return {
        "current_step": Step.VERIFY_ROLE.value,
        "messages": state["messages"] + [AIMessage(content="What is your role?")]
    }
def verify_role(state: AgentState):
    """Verify the user's role"""
    user_input = str(state["messages"][-1].content)
    # valid_role = is_valid_role(user_input)
    valid_role = True
    if not valid_role:
        return {
            "current_step": Step.VERIFY_ROLE.value,
            "messages": state["messages"] + [AIMessage(content="That is not a valid role. Please try again.")]
        }
    # TODO db write
    return {
        "current_step": Step.VERIFY_CONTACT.value,
        "messages": state["messages"] + [AIMessage(content="That is a valid role. Thank you!\nWhat is your contact information?")]
    }

def ask_contact(state: AgentState):
    """Ask the user for their contact information"""
    return {
        "current_step": Step.VERIFY_CONTACT.value,
        "messages": state["messages"] + [AIMessage(content="What is your contact information?")]
    }

def verify_contact(state: AgentState):
    """Verify the user's contact information"""
    user_input = str(state["messages"][-1].content)
    # valid_contact = is_valid_contact(user_input)
    valid_contact = True
    # TODO db write
    if not valid_contact:
        return {
            "current_step": Step.VERIFY_CONTACT.value,
            "messages": state["messages"] + [AIMessage(content="That is not a valid contact information. Please try again.")]
        }
    return {
        "current_step": "",
        "current_agent": "",
        "messages": state["messages"] + [AIMessage(content="Thank you for onboarding!")]
    }

def fallback(state: AgentState):
    """Fallback step for the Audience Onboarder Agent"""
    default_message = """
    [Unclear Intent]
    I am here to help you onboard as an audience. I can log your name, role, and contact information.
    """
    return {
        "current_step": Step.FALLBACK.value,
        "messages": state["messages"] + [AIMessage(content=default_message)]
    }

def build_audience_onboarder_graph():
    graph = StateGraph(AgentState)

    graph.add_node(audience_onboarder_agent)
    for step in Step:
        graph.add_node(globals()[step.value])

    graph.add_edge(START, "audience_onboarder_agent")

    graph.add_conditional_edges(
        "audience_onboarder_agent",
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


def debugprint(state):
    print("\n" + "=" * 40)
    print(f"current_agent: {state['current_agent']}")
    print(f"current_step: {state['current_step']}")
    print(f"last_message: {state['messages'][-1].content}")
    print("=" * 40 + "\n")

if __name__ == "__main__":
    graph = build_audience_onboarder_graph()
    new_state = initialize_agent_state("user123")
    new_state["messages"] = [HumanMessage(content="hello")]
    result = graph.invoke(new_state)

    while True:
        print(result["messages"][-1].content)
        answer = input("> ")
        new_state = AgentState(**result)
        new_state["messages"].append(HumanMessage(content=answer))

        result = graph.invoke(new_state)
        new_state = result

        debugprint(result)