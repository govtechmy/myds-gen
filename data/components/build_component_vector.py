import os
import json
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]


def main():
    with open("data/components/myds.json") as f:
        data = json.load(f)

    docs = [
        Document(
            id=i,
            metadata={"component_name": x["name"]},
            page_content=f'{x["name"]} - {x["description"]}',
        )
        for i, x in enumerate(data)
    ]
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
    )
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(documents=docs)
    vector_store.dump("data/components/comp_vector.json")

if __name__ == "__main__":
    main()
