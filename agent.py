from datetime import datetime
from pprint import pformat
from langgraph_models import * 
from langchain.schema import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from chat_helpers import *
from uuid import uuid4
import os
from dotenv import load_dotenv
from github import build_github_graph
from uagents import Context, Protocol, Agent
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    StartSessionContent,
    EndSessionContent,
    AgentContent,
    TextContent,
    chat_protocol_spec,
)
load_dotenv()

graph = build_github_graph()

agent = Agent(
    name="Personal Brand Orchestrator",
    seed=os.getenv("AGENT_SEED"),
    port=8001,
    mailbox=True,
)
protocol = Protocol(spec=chat_protocol_spec)

@protocol.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )

    if is_asione_message(msg):
        response = "This was a ASI:One message"
        ctx.logger.info("Trying to start langgraph flow")
        continue_with_github: AgentState = {"current_step":1,"current_agent":"github_agent","messages": [HumanMessage(content="Post to github for me."), AIMessage(content="Waiting for confirm.")]}

        current_count = ctx.storage.get("count") or 0
        ctx.storage.set("count", current_count + 1)

        ctx.logger.info(get_chat_id_from_message(msg))
        # result = graph.invoke(continue_with_github)
        # hi = pformat(msg)
        # ctx.logger.info(hi)
        await ctx.send(sender, ChatMessage(
            timestamp=datetime.now(),
            msg_id=uuid4(),
            content=[
                TextContent(type="text", text=str(current_count)),

                # This will end the chat session after one interaction
                # EndSessionContent(type="end-session") 
            ]
        ))


@protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    pass

# I believe you have to have this to register it to AgentVerse
agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()