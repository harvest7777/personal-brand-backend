from datetime import datetime
from brand_agent.brand_agent_helpers import *
from utils.chat_helpers import *
from uuid import uuid4
import os
from chroma.chroma_helpers import *
from dotenv import load_dotenv
from uagents.setup import fund_agent_if_low
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
llm = ChatOpenAI(model="gpt-4o-mini")


agent = Agent(
    name="Ryans Brand Agent",
    seed=os.getenv("BRAND_AGENT_SEED"),
    port=8002,
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

    # region Querying the database for the most relevant facts and generating a response
    # TODO get this dynamically, this is the agent (user id) that is tied to this brand agent
    agent_id = "agent1q29tg4sgdzg33gr7u63hfemq4hk54thsya3s7kygurrxg3j8p8f2qlnxz9f"
    facts = get_most_relevant_facts(agent_id, human_input, 1)
    ai_response = answer_query_with_facts(facts, human_input, llm)
    # endregion

    # region Sending the response back to the user through ASI:One
    if is_sent_by_asione(msg):
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


@protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    pass

# I believe you have to have this to register it to AgentVerse
agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()