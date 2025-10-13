from datetime import datetime
from langgraph_logic.github import build_github_graph
from pprint import pformat
from langgraph_logic.models import * 
from langchain.schema import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from utils.chat_helpers import *
from uuid import uuid4
import os
from dotenv import load_dotenv
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

    chat_id = get_chat_id_from_message(msg)
    if chat_id is None:
        ctx.logger.error("No chat id found in message")
        return

    chat_data = ctx.storage.get(chat_id) 
    ctx.logger.info(f"Chat data: {pformat(chat_data)}")

    if is_asione_message(msg):
        await ctx.send(sender, ChatMessage(
            timestamp=datetime.now(),
            msg_id=uuid4(),
            content=[
                TextContent(type="text", text="Hello"),

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