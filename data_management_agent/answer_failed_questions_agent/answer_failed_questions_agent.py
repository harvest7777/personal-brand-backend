from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from data_management_agent.models import *
from data_management_agent.data_management_agent_definitions import Agent
from data_management_agent.answer_failed_questions_agent.answer_failed_questions_steps import Step
from data_management_agent.answer_failed_questions_agent.answer_failed_questions_helpers import (
    get_all_failed_questions,
    get_question_by_id,
    get_random_question,
    delete_question,
    format_questions_list,
    save_answer_as_fact,
    wants_random_question,
    delete_all_failed_questions
)
from chroma.chroma_helpers import insert_question
from brand_agent.brand_agent_helpers import get_brand_agent_id_from_asi_one_id
from shared_clients.llm_client import shared_llm
from langchain_core.messages import SystemMessage, HumanMessage

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
    print("brand_agent_id", brand_agent_id)
    
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
    """Ask the user if they want a random question or a specific question by ID, then show the question and list remaining"""
    user_input = str(state["messages"][-1].content).strip()
    asi_one_id = state["asi_one_id"]
    brand_agent_id = get_brand_agent_id_from_asi_one_id(asi_one_id)
    
    if not brand_agent_id:
        return {
            "current_step": "",
            "current_agent": "",
            "messages": state["messages"] + [AIMessage(content="Could not find your personal brand agent.")]
        }
    
    # Use LLM to determine if user wants random question
    wants_random = wants_random_question(user_input, state["messages"])
    
    question = None
    if wants_random:
        question = get_random_question(brand_agent_id)
        if not question:
            return {
                "current_step": "",
                "current_agent": "",
                "messages": state["messages"] + [AIMessage(content="No more questions to answer!")]
            }
    else:
        # Try to get question by ID
        question = get_question_by_id(user_input)
        if not question:
            return {
                "current_step": Step.ASK_QUESTION.value,
                "current_agent": Agent.ANSWER_FAILED_QUESTIONS.value,
                "messages": state["messages"] + [AIMessage(content="I didn't find a question with that ID. Please paste a valid question ID or ask for a random question.")]
            }
    
    # Get remaining questions (excluding the one we're about to show)
    remaining_questions = get_all_failed_questions(brand_agent_id)
    remaining_questions = [q for q in remaining_questions if q["id"] != question["id"]]
    remaining_text = format_questions_list(remaining_questions, limit=5)
    
    # Show the question, list remaining, and ask for answer
    message = f"Here's the question:\n\n{question['question']}\n\n"
    
    if remaining_questions:
        message += f"Here are the next 5 remaining questions:\n\n{remaining_text}\n\n"
    
    message += "Please provide your answer to the question above."
    
    return {
        "current_step": Step.HANDLE_ANSWER.value,
        "current_agent": Agent.ANSWER_FAILED_QUESTIONS.value,
        "answer_failed_questions_agent_state": AnswerFailedQuestionsAgentState(
            current_question_id=question["id"],
            current_question=question["question"]
        ),
        "messages": state["messages"] + [AIMessage(content=message)]
    }

def handle_answer(state: AgentState):
    """Handle the user's answer to a question, then list remaining questions and ask again"""
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
    
    # Get remaining questions
    remaining_questions = get_all_failed_questions(brand_agent_id)
    
    message = f"Thanks! I've recorded your response and marked that question as complete.\n\n"
    
    if remaining_questions:
        # List remaining questions and ask which one to answer next
        remaining_text = format_questions_list(remaining_questions, limit=5)
        message += f"Here are the next 5 remaining questions:\n\n{remaining_text}\n\n"
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
    else:
        # All done
        message += "All questions have been answered!"
        return {
            "current_step": "",
            "current_agent": "",
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
    
    # Test configuration
    brand_agent_id = "agent1qgerajmgluncfslmdmrgxww463ntt4c90slr0srq4lcc9vmyyavkyg2tzh7"
    asi_one_id = "agent1q29tg4sgdzg33gr7u63hfemq4hk54thsya3s7kygurrxg3j8p8f2qlnxz9f"
    graph = build_answer_failed_questions_graph()
    
    def reset_state():
        """Delete all failed questions for the test brand agent"""
        delete_all_failed_questions(brand_agent_id)
        print("✓ Reset: Deleted all failed questions")
    
    def add_test_questions():
        """Add some test questions"""
        test_questions = [
            "What is your favorite programming language?",
            "How many years of experience do you have?",
            "What is your biggest achievement?"
        ]
        for question in test_questions:
            insert_question(asi_one_id, question, brand_agent_id)
        print(f"✓ Added {len(test_questions)} test questions")
    
    def run_test(test_name: str, user_messages: list[str]):
        """Run a test with given user messages"""
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print(f"{'='*60}")
        
        reset_state()
        add_test_questions()
        
        state = initialize_agent_state(asi_one_id)
        
        for i, user_msg in enumerate(user_messages):
            print(f"\n--- Step {i+1} ---")
            print(f"User: {user_msg}")
            state["messages"].append(HumanMessage(content=user_msg))
            result = graph.invoke(state)
            state = AgentState(**result)
            
            ai_response = result["messages"][-1].content
            print(f"AI: {ai_response}")
        
        print(f"\n{'='*60}\n")
    
    # Test 1: Just getting the failed questions
    run_test(
        "Getting failed questions",
        ["what are my remaining questions?"]
    )
    
    # Test 2: Trying to pick a random one to answer
    run_test(
        "Picking a random question",
        ["what are my remaining questions?", "random"]
    )
    
    # Test 3: Picking by UUID
    reset_state()
    add_test_questions()
    questions = get_all_failed_questions(brand_agent_id)
    if questions:
        question_id = questions[0]["id"]
        print(f"\n{'='*60}")
        print(f"TEST: Picking by UUID")
        print(f"{'='*60}")
        
        state = initialize_agent_state(asi_one_id)
        state["messages"].append(HumanMessage(content="what are my remaining questions?"))
        result = graph.invoke(state)
        state = AgentState(**result)
        print(f"User: what are my remaining questions?")
        print(f"AI: {result['messages'][-1].content}")
        
        print(f"\n--- Step 2 ---")
        print(f"User: {question_id}")
        state["messages"].append(HumanMessage(content=question_id))
        result = graph.invoke(state)
        print(f"AI: {result['messages'][-1].content}")
        print(f"\n{'='*60}\n")
    else:
        print("No questions to test UUID picking")
    
    # Test 4: Picking by UUID then answering
    reset_state()
    add_test_questions()
    questions = get_all_failed_questions(brand_agent_id)
    if questions:
        question_id = questions[0]["id"]
        print(f"\n{'='*60}")
        print(f"TEST: Picking by UUID then answering")
        print(f"{'='*60}")
        
        state = initialize_agent_state(asi_one_id)
        state["messages"].append(HumanMessage(content="what are my remaining questions?"))
        result = graph.invoke(state)
        state = AgentState(**result)
        print(f"User: what are my remaining questions?")
        print(f"AI: {result['messages'][-1].content}")
        
        print(f"\n--- Step 2 ---")
        print(f"User: {question_id}")
        state["messages"].append(HumanMessage(content=question_id))
        result = graph.invoke(state)
        state = AgentState(**result)
        print(f"AI: {result['messages'][-1].content}")
        
        print(f"\n--- Step 3 ---")
        answer = "Python is my favorite programming language"
        print(f"User: {answer}")
        state["messages"].append(HumanMessage(content=answer))
        result = graph.invoke(state)
        print(f"AI: {result['messages'][-1].content}")
        print(f"\n{'='*60}\n")
    else:
        print("No questions to test UUID picking and answering")

