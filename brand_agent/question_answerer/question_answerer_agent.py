from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from brand_agent.brand_agent_helpers import *
from brand_agent.brand_agent_helpers import *
from brand_agent.brand_agent_state_model import BrandAgentState, initialize_agent_state
from brand_agent.question_answerer.question_answerer_steps import Step
from shared_clients.llm_client import shared_llm
from chroma.chroma_helpers import get_most_relevant_facts

def question_answerer_agent(state: BrandAgentState):
    """Initial entry point for the Question Answerer Agent, it will determine the next step to display to the user"""
    current_step = state.get("current_step")
    is_valid_step = current_step in [s.value for s in Step]

    if not current_step or not is_valid_step:
        # Answer question step will be our fallback
        current_step = Step.ANSWER_QUESTION.value
    return {
        "current_step": current_step,
        "messages": state["messages"]
    }

def answer_question(state: BrandAgentState):
    """Answer the question"""
    brand_agent_id = state["brand_agent_id"]
    asi_one_id = get_asi_one_id_from_brand_agent_id(brand_agent_id)

    human_input = str(state["messages"][-1].content)
    facts = get_most_relevant_facts(asi_one_id, human_input, 3)
    ai_response = answer_query_with_facts(facts, human_input, shared_llm)
    if not facts:
        supabase.from_("failed_questions").insert({
            "personal_brand_agent_id": brand_agent_id,
            "audience_asi_one_id": asi_one_id,
            "question": human_input,
        }).execute()
    return {
        "current_step": Step.ANSWER_QUESTION.value,
        "messages": state["messages"] + [AIMessage(content=ai_response)]
    }


def build_question_answerer_graph():
    graph = StateGraph(BrandAgentState)

    graph.add_node(question_answerer_agent)
    for step in Step:
        graph.add_node(globals()[step.value])

    graph.add_edge(START, "question_answerer_agent")

    graph.add_conditional_edges(
        "question_answerer_agent",
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
    graph = build_question_answerer_graph()
    state = initialize_agent_state(
        asi_one_id="agent1qdnhwqv3ekrzcuk597nrzc8xh9eyurlwvsrzzrytr6cl87zuwfuayh4xq6g",
        brand_agent_id="agent1qgerajmgluncfslmdmrgxww463ntt4c90slr0srq4lcc9vmyyavkyg2tzh7"
    )
    state["messages"] = [HumanMessage(content="is ryan open to work?")]
    result = graph.invoke(state)
    print(result)

