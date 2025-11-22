from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from data_management_agent.models import *
from data_management_agent.data_management_agent_definitions import Agent
from data_management_agent.answer_failed_questions_agent.answer_failed_questions_steps import Step
from data_management_agent.answer_failed_questions_agent.answer_failed_questions_helpers import (
    get_brand_agent_id_from_asi_one_id,
    get_all_failed_questions,
    get_question_by_id,
    get_random_question,
    delete_question,
    format_questions_list,
    save_answer_as_fact
)

def answer_failed_questions_agent(state: AgentState):
    """Initial entry point for the Answer Failed Questions Agent, it will determine the next step to display to the user"""
    current_step = state["current_step"]
    is_valid_step = current_step in [s.value for s in Step]

    if not current_step or not is_valid_step:
        # Start by listing questions
        current_step = Step.LIST_QUESTIONS.value

    return {
        "current_step": current_step,
        "current_agent": Agent.ANSWER_FAILED_QUESTIONS.value,
        "messages": state["messages"]
    }

def list_questions(state: AgentState):
    """List all failed questions"""
    asi_one_id = state["asi_one_id"]
    brand_agent_id = get_brand_agent_id_from_asi_one_id(asi_one_id)
    
    if not brand_agent_id:
        return {
            "current_step": "",
            "current_agent": "",
            "messages": state["messages"] + [AIMessage(content="Could not find your personal brand agent. Please deploy one first.")]
        }
    
    questions = get_all_failed_questions(brand_agent_id)
    
    if not questions:
        return {
            "current_step": "",
            "current_agent": "",
            "messages": state["messages"] + [AIMessage(content="Great! You don't have any failed questions. All questions have been answered!")]
        }
    
    # Format all questions with IDs
    questions_text = format_questions_list(questions)
    
    message = f"Here are the questions I couldn't answer:\n\n{questions_text}\n\nIf you'd like to answer some manually, just paste the IDs!\n\nOr, I could give you a random question to answer?"
    
    return {
        "current_step": Step.ASK_QUESTION.value,
        "current_agent": Agent.ANSWER_FAILED_QUESTIONS.value,
        "messages": state["messages"] + [AIMessage(content=message)]
    }

def ask_question(state: AgentState):
    """Ask the user if they want a random question or a specific question by ID"""
    user_input = str(state["messages"][-1].content).strip().lower()
    asi_one_id = state["asi_one_id"]
    brand_agent_id = get_brand_agent_id_from_asi_one_id(asi_one_id)
    
    if not brand_agent_id:
        return {
            "current_step": "",
            "current_agent": "",
            "messages": state["messages"] + [AIMessage(content="Could not find your personal brand agent.")]
        }
    
    # Check if user wants a random question
    if "random" in user_input or "yes" in user_input or "sure" in user_input or "ok" in user_input:
        random_q = get_random_question(brand_agent_id)
        if not random_q:
            return {
                "current_step": "",
                "current_agent": "",
                "messages": state["messages"] + [AIMessage(content="No more questions to answer!")]
            }
        
        return {
            "current_step": Step.HANDLE_ANSWER.value,
            "current_agent": Agent.ANSWER_FAILED_QUESTIONS.value,
            "answer_failed_questions_agent_state": AnswerFailedQuestionsAgentState(
                current_question_id=random_q["id"],
                current_question=random_q["question"]
            ),
            "messages": state["messages"] + [AIMessage(content=random_q["question"])]
        }
    
    # Check if user provided an ID
    # Try to get question by ID
    question = get_question_by_id(user_input)
    
    if question:
        return {
            "current_step": Step.HANDLE_ANSWER.value,
            "current_agent": Agent.ANSWER_FAILED_QUESTIONS.value,
            "answer_failed_questions_agent_state": AnswerFailedQuestionsAgentState(
                current_question_id=question["id"],
                current_question=question["question"]
            ),
            "messages": state["messages"] + [AIMessage(content=question["question"])]
        }
    
    # If we get here, user input wasn't recognized
    return {
        "current_step": Step.ASK_QUESTION.value,
        "current_agent": Agent.ANSWER_FAILED_QUESTIONS.value,
        "messages": state["messages"] + [AIMessage(content="I didn't understand that. Please paste a question ID or ask for a random question.")]
    }

def handle_answer(state: AgentState):
    """Handle the user's answer to a question"""
    user_answer = str(state["messages"][-1].content)
    current_question_id = state["answer_failed_questions_agent_state"]["current_question_id"]
    current_question = state["answer_failed_questions_agent_state"]["current_question"]
    asi_one_id = state["asi_one_id"]
    brand_agent_id = get_brand_agent_id_from_asi_one_id(asi_one_id)
    
    if not current_question_id or not current_question:
        return {
            "current_step": Step.ASK_QUESTION.value,
            "current_agent": Agent.ANSWER_FAILED_QUESTIONS.value,
            "messages": state["messages"] + [AIMessage(content="I lost track of which question you were answering. Let me get you a new one.")]
        }
    
    # Save the answer as a fact
    save_answer_as_fact(asi_one_id, current_question, user_answer)
    
    # Delete the question
    delete_question(current_question_id)
    
    # Get next 5 questions
    remaining_questions = get_all_failed_questions(brand_agent_id)
    next_questions_text = format_questions_list(remaining_questions, limit=5)
    
    message = f"Thanks! I've recorded your response and marked that question as complete. "
    
    if remaining_questions:
        message += f"Here are the next 5 questions:\n\n{next_questions_text}\n\n"
    else:
        message += "All questions have been answered!\n\n"
    
    message += "Feel free to paste another ID or tell me to give you a random question."
    
    return {
        "current_step": Step.ASK_QUESTION.value,
        "current_agent": Agent.ANSWER_FAILED_QUESTIONS.value,
        "answer_failed_questions_agent_state": AnswerFailedQuestionsAgentState(
            current_question_id="",
            current_question=""
        ),
        "messages": state["messages"] + [AIMessage(content=message)]
    }

def build_answer_failed_questions_graph():
    graph = StateGraph(AgentState)
    
    graph.add_node(answer_failed_questions_agent)
    for step in Step:
        graph.add_node(globals()[step.value])
    
    graph.add_edge(START, "answer_failed_questions_agent")
    
    graph.add_conditional_edges(
        "answer_failed_questions_agent",
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
    graph = build_answer_failed_questions_graph()
    
    new_chat: AgentState = initialize_agent_state("agent1q29tg4sgdzg33gr7u63hfemq4hk54thsya3s7kygurrxg3j8p8f2qlnxz9f")
    result = graph.invoke(new_chat)
    print("result", result)

