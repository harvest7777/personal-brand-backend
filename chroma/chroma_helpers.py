from chroma.chroma_models import *
from chroma.chroma_constants import *
import chromadb
import uuid
from datetime import datetime

chroma_client = chromadb.PersistentClient()
collection = chroma_client.get_or_create_collection(name=COLLECTION)

def insert_resume_fact(agent_id: str, fact: str) -> ChromaDocument:
    """Takes a resume fact and embeds it with additional metadata needed for chroma, returns the inserted document"""

    # TODO delete all the old resume facts if the user is uploading again to avoid stale information
    new_doc = ChromaDocument(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        document=fact,
        source=Source.RESUME.value,
        time_logged=datetime.now().astimezone()
    )

    # Insert into Chroma
    collection.add(
        ids=[new_doc.id],
        documents=[new_doc.document],
        metadatas=[{
            "source": new_doc.source,
            "user_id": new_doc.agent_id,
            "time_logged": new_doc.time_logged.isoformat()
        }]
    )

    return new_doc