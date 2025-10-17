from calendar import c
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langchain.schema import AIMessage, HumanMessage
from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()
url: str = os.environ.get("SUPABASE_URL") or ""
key: str = os.environ.get("SUPABASE_KEY") or ""
supabase: Client = create_client(url, key)

llm = ChatOpenAI(model="gpt-4o-mini")

def call_model(state):
    response = llm.invoke(state["messages"])
    return {
        "messages": state["messages"] + [response]
    }

def is_valid_name(user_input: str) -> bool:
    """Check if the user's message is an answer to 'What is your full name?'"""
    response = llm.invoke([
        HumanMessage(content=f"""
        You are validating user input.

        The user was asked: "What is your full name?"

        Determine if their response below *answers that question* by providing a name 
        (e.g., "My name is John", "I'm Alice Smith", "Call me Peter", etc.).

        Respond with only 'yes' or 'no'.

        User response: "{user_input}"
        """)
    ])
    answer = response.content.strip().lower()  # type: ignore
    return answer == "yes"


def extract_name(user_input: str):
    """Extract the full name from the user's input"""
    response = llm.invoke([
        HumanMessage(content=f"""
        Extract the full name from the following text.
        Respond with only the full name and nothing else.

        Text: "{user_input}"
        """)
    ])

    extracted_name = response.content.strip()  # type: ignore
    return extracted_name

def parse_resume(resume_contents: str):


if __name__ == "__main__":
    print(is_valid_name("my name is john doe"))