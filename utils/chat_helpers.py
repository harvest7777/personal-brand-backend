from uagents_core.contrib.protocols.chat import ChatMessage, MetadataContent, TextContent

def is_asione_message(msg: ChatMessage):
    """Determines if a ChatMessage was sent by ASI:One"""
    return isinstance(msg.content[-1], MetadataContent)

def is_user_message(msg: ChatMessage):
    """Determines if a ChatMessage was sent by a user through Chat Protocol"""
    return isinstance(msg.content[-1], TextContent)

def get_chat_id_from_message(msg: ChatMessage):
    """Extracts the chat id from a ChatMessage if it was sent by ASI:One"""
    chat_id = None
    for content in msg.content:
        if isinstance(content, MetadataContent):
            if "x-session-id" in content.metadata:
                chat_id = content.metadata["x-session-id"]
                break
    return chat_id