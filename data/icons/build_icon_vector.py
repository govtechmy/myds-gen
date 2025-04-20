import os
import re
import argparse
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]


def extract_icon_name(file_path, file_name):
    with open(os.path.join(file_path, file_name)) as f:
        data = f.read()
    name = re.findall(
        r"export const ([\w]*): FunctionComponent<\n? *?SVGProps<SVGSVGElement>\n?>",
        data,
    )
    return name[0]


def get_icon_names(file_path):
    icon_files = [i for i in os.listdir(file_path) if ".tsx" in i]
    icon_names = [extract_icon_name(file_path, i) for i in icon_files]
    return icon_names


def main(file_path):
    icon_names = get_icon_names(file_path)

    docs = [
        Document(
            id=i,
            page_content=x,
        )
        for i, x in enumerate(icon_names)
    ]
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
    )
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(documents=docs)
    vector_store.dump("data/icons/icon_vector.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mydspath", type=str)
    args = parser.parse_args()
    icon_path = os.path.join(args.mydspath, "packages/react/src/icons")
    main(file_path=icon_path)
