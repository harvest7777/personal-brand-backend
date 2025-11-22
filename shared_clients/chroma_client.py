import chromadb
from chroma.chroma_constants import *
from dotenv import load_dotenv

load_dotenv()

chroma_client = chromadb.PersistentClient()
facts_collection = chroma_client.get_or_create_collection(name=FACTS)
questions_collection = chroma_client.get_or_create_collection(name=QUESTIONS)