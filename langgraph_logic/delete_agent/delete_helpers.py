from langchain_core.messages import HumanMessage
from langgraph_logic.shared_clients.llm_client import shared_llm

def is_valid_delete_request(user_input: str) -> bool:
    """Check if the user's message is a valid delete request"""
    response = shared_llm.invoke([
        HumanMessage(content=f"""
        You are validating user input.

        The user was asked: "What data would you like to delete?"

        Determine if their response below *answers that question* by providing the data to delete.

        Respond with only 'yes' or 'no'.

        User response: "{user_input}"
        """)
    ])
    answer = response.content.strip().lower()  # type: ignore
    return answer == "yes"

def is_affirmative_response(user_input: str) -> bool:
    """Check if the user's message is an affirmative response"""
    response = shared_llm.invoke([
        HumanMessage(content=f"""
        You are validating user input.

        Did the user answer affirmatively to the question: "Would you like to delete the data?"

        Respond with only 'yes' or 'no'.

        User response: "{user_input}"
        """)
    ])
    answer = response.content.strip().lower()  # type: ignore
    return answer == "yes"

if __name__ == "__main__":
    print(is_valid_delete_request("I want to delete my data"))
    print(is_valid_delete_request("I want to delete my data about my work experience at Walmart"))
    print(is_valid_delete_request("i wanna delete datas about my high school"))