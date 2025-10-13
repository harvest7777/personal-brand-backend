from langchain.schema import HumanMessage, AIMessage
from langgraph_logic.models import *
from database.agent_db_models import *
from pprint import pprint
from langgraph_logic.main import graph
from fastapi import FastAPI
from utils.data_serialization_helpers import *

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/chat")
async def handeChat(agent_state_body: JsonAgentState):
    langgraph_state = jsonAgentStateToLangGraph(agent_state_body)
    result = graph.invoke(langgraph_state)
    print(result)

    return {"state": result}

if __name__ == "__main__":
    print("Running from api.py")
    continue_with_github: AgentState = {"current_step":1,"current_agent":"github_agent","messages": [HumanMessage(content="Post to github for me."), AIMessage(content="Waiting for confirm.")]}
    result = graph.invoke(continue_with_github)
    pprint(result, indent=2)