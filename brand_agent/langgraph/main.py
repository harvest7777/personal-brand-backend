from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from langgraph_logic.models import *
from langgraph_logic.router_helpers import *
from brand_agent.langgraph.question_answerer.question_answerer_agent import build_question_answerer_graph
from brand_agent.langgraph.brand_agent_definitions import Agent

# --- Intent Router ---
def intent_router(state: AgentState):
    if user_wants_to_exit_flow(state):
        return {"current_agent": "END", "current_step": "", "messages": [AIMessage(content="Gotcha, goodbye!")]}

    # Continuing where we left off, user is already working with an agent and is in some step
    if "current_agent" in state and state["current_agent"] in [agent.value for agent in Agent]:
        return {"current_agent": state["current_agent"]}

    # New conversation or the user has exited one of the other agents 
    classified_agent = classify_intent(state)

    return {"current_agent": classified_agent.value}


def fallback_agent(state: AgentState):
    # TODO fetch the user's name from db for fallback
    default_message = """
    [Unclear Intent]
    I am a personal brand agent. I can answer questions on behalf of [user would go here]'s personal brand.
    """
    return {
        "messages": [AIMessage(content=default_message)],
        "current_agent": "",
        "current_step": 1
    }

# --- Build Graph ---
def build_main_graph():
    graph = StateGraph(AgentState)
    graph.add_node(intent_router)

    question_answerer_agent = build_question_answerer_graph()

    graph.add_node(Agent.QUESTION_ANSWERER.value, question_answerer_agent)
    graph.add_node(Agent.FALLBACK.value, fallback_agent)

    graph.add_edge(START, "intent_router")

    graph.add_conditional_edges(
        "intent_router",
        lambda state: state["current_agent"],
        {
            **{agent.value: agent.value for agent in Agent},
            "END": END,
        },
    )

    for node in [agent.value for agent in Agent]:
        graph.add_edge(node, END)

    graph = graph.compile()
    return graph


# --- Test ---
def debugprint(state):
    print("\n" + "=" * 40)
    print(f"current_agent: {state['current_agent']}")
    print(f"current_step: {state['current_step']}")
    print(f"last_message: {state['messages'][-1].content}")
    print("=" * 40 + "\n")

if __name__ == "__main__":
    graph = build_main_graph()
    new_state = initialize_agent_state("user123")
    new_state["messages"] = [HumanMessage(content="i want to feed information.")]
    result = graph.invoke(new_state)

    while True:
        print(result["messages"][-1].content)
        answer = input("> ")
        new_state = AgentState(**result)
        new_state["messages"].append(HumanMessage(content=answer))

        result = graph.invoke(new_state)
        new_state = result

        debugprint(result)