from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()
url: str = os.environ.get("SUPABASE_URL") or ""
key: str = os.environ.get("SUPABASE_KEY") or ""
supabase: Client = create_client(url, key)


def is_valid_agent_id(user_input: str, llm: ChatOpenAI) -> bool:
    """
    Check if the user input contains a valid agent_id, even if the user says something like 'my agent id is ...'.
    Uses an LLM to validate if the user's input contains a legitimate agent id.
    """
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage


    response = llm.invoke([
        HumanMessage(content=f"""
You are validating user input.

The user was asked: "What is the id of the agent that will be your personal brand?"

Determine if their response below *answers that question* by providing an agent id (e.g., agent1qt3qh62838nhu4u7j86azn55ylvfm767d9rhk5lae4qe8lnyspvhu7zxrsx), 
even if it's part of a sentence like "My agent id is agent12345" or similar.

Respond with only 'yes' or 'no'.

User response: "{user_input}"
        """)
    ])
    answer = response.content.strip().lower() # type: ignore
    return answer == "yes"


def extract_agent_id(user_input: str) -> str:
    """
    Extract the agent_id from the user's input.
    Agent IDs look like: agent1qt3qh62838nhu4u7j86azn55ylvfm767d9rhk5lae4qe8lnyspvhu7zxrsx
    Returns the first found agent_id, or an empty string if none found.
    """
    import re
    match = re.search(r"agent[a-zA-Z0-9]+", user_input)
    return match.group(0) if match else ""

if __name__ == "__main__":
    from langgraph_logic.llm import shared_llm
    print("Deploy helpers")
    print(is_valid_agent_id("My agent id is agent1qt3qh62838nhu4u7j86azn55ylvfm767d9rhk5lae4qe8lnyspvhu7zxrsx", shared_llm))