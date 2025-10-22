import chromadb
from chroma.chroma_constants import *
from dotenv import load_dotenv

load_dotenv()

chroma_client = chromadb.PersistentClient()
collection = chroma_client.get_or_create_collection(name=COLLECTION)