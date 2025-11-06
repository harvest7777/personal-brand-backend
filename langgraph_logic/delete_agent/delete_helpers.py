from langchain_core.messages import HumanMessage
from langgraph_logic.shared_clients.llm_client import shared_llm
from chroma.shared_chroma_client import collection

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

def to_delete_from_user_input(user_input: str) -> list[str]:
    """Extract the data to delete from the user's input"""
    documents = []
    result = collection.query(query_texts=user_input, n_results=5)
    for i in range(len(result["documents"])): # type: ignore
        if result["distances"][i][0] <= 2: # type: ignore
            documents.append(result["documents"][i][0]) # type: ignore

    return documents

if __name__ == "__main__":
    docs = to_delete_from_user_input("college")
    print(docs)