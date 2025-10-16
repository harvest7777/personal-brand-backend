from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langchain.schema import AIMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")
def call_model(state):
    response = llm.invoke(state["messages"])
    return {
        "messages": state["messages"] + [response]
    }

