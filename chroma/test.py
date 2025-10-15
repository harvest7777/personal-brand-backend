import chromadb
chroma_client = chromadb.PersistentClient()

collection = chroma_client.get_collection(name="my_collection")
# collection.add(
#     ids=["id1", "id2"],
#     documents=[
#         "This is a document about pineapple",
#         "This is a document about oranges"
#     ]
# )
collection.add(
    ids=["id1", "id2", "id3"],
    documents=["lorem ipsum...", "doc2", "doc3"],
    metadatas=[{"chapter": 3, "verse": 16}, {"chapter": 3, "verse": 5}, {"chapter": 29, "verse": 11}]
)

results = collection.query(
    query_texts=["lorem "], # Chroma will embed this for you
    n_results=1 
)




if __name__ == "__main__":
    print("ChromaDB client created:", chroma_client)
    print(results)
