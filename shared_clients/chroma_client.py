import chromadb
from chroma.chroma_constants import *
from dotenv import load_dotenv

load_dotenv()

# chroma_client = chromadb.PersistentClient()
chroma_client = chromadb.HttpClient(host='localhost', port=8000)
facts_collection = chroma_client.get_or_create_collection(name=FACTS)
failed_questions_collection = chroma_client.get_or_create_collection(name=QUESTIONS)