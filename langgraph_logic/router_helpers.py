from langgraph_logic.models import AgentState
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph_logic.agents import *

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

def classify_intent(state: AgentState) -> Agent:
    """
    Determines the next agent to route the user's request to based on 
    conversation history
    """
    # Access full conversation history
    messages = state["messages"]
    
    # You can use the entire conversation for context
    # This helps with multi-turn conversations and context-aware routing
    recent_context = messages[-5:]  # Last 5 messages

    agent_list = [
        f"{agent.value}: {description}"
        for agent, description in AGENT_DESCRIPTIONS.items()
    ]
    agent_list_str = "\n".join(agent_list)

    route_prompt = (
        f"You are a smart router for a multi-agent system. "
        f"Your job is to select the most appropriate agent to handle the user's intent, "
        f"using their recent messages for context. "
        f"Here are the available agents:\n\n"
        f"{agent_list_str}\n\n"
        f"Recent conversation context:\n"
    )

    for msg in recent_context:
        role = "User" if getattr(msg, "role", None) == "user" or msg.__class__.__name__ == "HumanMessage" else "Assistant"
        route_prompt += f"{role}: {msg.content}\n"

    route_prompt += (
        "\nBased on the user's request and the context, "
        "reply ONLY with the agent key (from the available values above, e.g., 'github_agent', 'onboarding_agent', 'resume_agent', etc.) "
        "that should handle this request. "
        "If the user's message is just a greeting (for example, 'hey', 'hello', 'hi'), or is otherwise ambiguous and not related to any specific action, route to 'fallback_agent'. "
        "If you are unsure, select 'fallback_agent'. "
        "Do not explain your answer."
    )

    llm_response = llm.invoke([{"role": "system", "content": route_prompt}])
    agent_key = llm_response.content.strip().split("\n")[0] # type: ignore

    # Defensive check to ensure the agent exists
    valid_agent_keys = [agent.value for agent in Agent]
    if agent_key not in valid_agent_keys:
        agent_key = Agent.FALLBACK

    return Agent(agent_key)

if __name__ == "__main__":
    new_chat: AgentState = {
        "asi_one_id": "",
        "current_step": "",
        "current_agent": "",
        "messages": [
            HumanMessage(content="hi"),
            AIMessage(content="Want to connect your linkedin?"),
            HumanMessage(content="yea")
        ]
    }
    print(classify_intent(new_chat).value)