from datetime import datetime
from langgraph_logic.main import build_main_graph
from langgraph_logic.models import * 
from utils.data_serialization_helpers import *
from utils.chat_helpers import *
from utils.db_helpers import *
from utils.state_helpers import *
from uuid import uuid4
from langchain_core.load import dumps, loads
from uagents.setup import fund_agent_if_low
import os
from dotenv import load_dotenv
from uagents import Context, Protocol, Agent
from agent.orchestrator_models import *
from langgraph_logic.shared_clients.composio_client import *
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)
load_dotenv()
graph = build_main_graph()

agent = Agent(
    name="Personal Brand Orchestrator",
    seed=os.getenv("AGENT_SEED"),
    port=8001,
    mailbox=True,
)

fund_agent_if_low(str(agent.wallet.address()))

protocol = Protocol(spec=chat_protocol_spec)

@protocol.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )

    # region Simple parsing input and getting chat metadata
    chat_id = get_chat_id_from_message(msg)
    human_input = get_human_input_from_message(msg)

    # This should never execute. If it does, something is very wrong lol
    if chat_id is None:
        ctx.logger.error("No chat id found in message")
        return

    # This should never execute. If it does, something is very wrong lol
    if human_input is None:
        ctx.logger.error("No human input found in message")
        return
    # endregion

    # region Initializing the langgraph state, invoking the graph, then updating the state
    asi_one_id = sender
    current_state = get_most_recent_state_from_agent_db(chat_id, ctx)

    if current_state is None:
        current_state = initialize_agent_state(asi_one_id)

    append_message_to_state(current_state, human_input)

    next_state = graph.invoke(current_state) # This will return a dict, NOT a state object

    json_result = dumps(next_state) # Has to be json to store in agent db
    ctx.storage.set(chat_id, json_result) # Save the new state to the DB
    # endregion

    # region Sending the response back to the user through ASI:One
    if is_sent_by_asione(msg):
        ai_response = next_state["messages"][-1].content

         # Save the updated state to the database
        await ctx.send(sender, ChatMessage(
            timestamp=datetime.now(),
            msg_id=uuid4(),
            content=[
                TextContent(type="text", text=ai_response),

                # This will end the chat session after one interaction
                # EndSessionContent(type="end-session") 
            ]
        ))

    # endregion


# need to define req and respo
@agent.on_rest_post("/connection_success", ForwardConnectionLink, ConnectionLinkForwardedResponse)
async def handle_post(ctx: Context, req: ForwardConnectionLink) -> ConnectionLinkForwardedResponse:
    ctx.logger.info("Received POST request")
    await ctx.send("agent1q29tg4sgdzg33gr7u63hfemq4hk54thsya3s7kygurrxg3j8p8f2qlnxz9f", ChatMessage(
        content=[
            TextContent(type="text", text=f"Connection link forwarded to {req.redirect_url}"),
        ]
    ))

    return ConnectionLinkForwardedResponse(
        success=True
    )

@protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    pass

# I believe you have to have this to register it to AgentVerse
agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()