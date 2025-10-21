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

def get_most_relevant_facts(asi_one_id: str, query: str, n: int) -> list[ChromaDocument]:
    """
    Retrieves the most relevant facts from Chroma for a specific agent based on a query.
    
    Args:
        agent_id: The agent ID to filter documents by
        query: The search query to find relevant documents
        n: The number of most relevant documents to return
    
    Returns:
        List of ChromaDocument objects that match the query and belong to the agent
    """
    # Query the collection with filtering by agent_id
    results = collection.query(
        query_texts=[query],
        n_results=n,
        where={"user_id": asi_one_id}
    )
    
    # Convert results to ChromaDocument objects
    documents = []
    if results['documents'] and results['documents'][0]:
        for i, doc_text in enumerate(results['documents'][0]):
            # Extract metadata
            metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
            doc_id = results['ids'][0][i] if results['ids'] and results['ids'][0] else str(uuid.uuid4())
            
            
            # Create ChromaDocument object
            chroma_doc = ChromaDocument(
                id=doc_id,
                agent_id=str(metadata['user_id']),
                document=doc_text,
                source=str(metadata['source']),
                time_logged=datetime.fromisoformat(str(metadata['time_logged']))
            )
            documents.append(chroma_doc)
    
    return documents

if __name__ == "__main__":
    agent_id = "agent1q29tg4sgdzg33gr7u63hfemq4hk54thsya3s7kygurrxg3j8p8f2qlnxz9f"
    query = "What are  skills?"

    facts = get_most_relevant_facts(agent_id, query, 1)
    print(facts)