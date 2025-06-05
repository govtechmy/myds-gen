import os
import json
import requests
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.load import load

from .langchain_schema import learnState

# os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]
DEP_TYPE = os.getenv("DEP_TYPE")
print(DEP_TYPE)
if DEP_TYPE == "serverless":
    BLOB_URL = os.getenv("BLOB_URL")


def retrieve_full(component_name):
    with open("data/components/myds.json") as f:
        data = json.load(f)
    return [i for i in data if component_name.lower() in i["name"].lower()]


def rag_icon(icon_name, gemini_api_key):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004", google_api_key=gemini_api_key
    )
    vector_store = InMemoryVectorStore(embeddings)
    if DEP_TYPE == "serverless":
        vector_path = f"{BLOB_URL}/icon_vector.json"
        vector = requests.get(vector_path).json()
        vector_store.store = load(vector)
    else:
        vector_path = "data/icons/icon_vector.json"
        vector_store = vector_store.load(vector_path, embeddings)

    return {
        "icon": icon_name,
        "retrieved": [
            i.page_content
            for i in vector_store.similarity_search(query=icon_name, k=10)
        ],
    }


def rag_component(query, gemini_api_key):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004", google_api_key=gemini_api_key
    )
    vector_store = InMemoryVectorStore(embeddings)
    if DEP_TYPE == "serverless":
        vector_path = f"{BLOB_URL}/comp_vector.json"
        vector = requests.get(vector_path).json()
        vector_store.store = load(vector)
    else:
        vector_path = "data/components/comp_vector.json"
        vector_store = vector_store.load(vector_path, embeddings)
    top2retrieved = [
        i.metadata["component_name"]
        for i in vector_store.similarity_search(query=query, k=4)
    ]
    top2retrieved_comps = [x for i in top2retrieved for x in retrieve_full(i)]

    return top2retrieved_comps


def comp_rag(state: learnState):
    new_prompt = state["enhanced_prompt"]

    comp_include = [
        rag_component(
            f"{i.library_component_name} - {i.library_component_usage_reason}",
            gemini_api_key=state["gemini_api_key"],
        )
        for i in new_prompt.components
    ]
    comp_include = [x for i in comp_include for x in i]
    comp_include = [i for n, i in enumerate(comp_include) if i not in comp_include[:n]]
    return {"comp_include": comp_include}


def gen_comp_task(state: learnState):
    prompt = state["enhanced_prompt"]
    design_data = state["design_plan"]
    component_task = {
        "name": f"{design_data.new_component_name}",
        "description": {
            "user": prompt,
            "llm": design_data.new_component_description,
        },
        "icons": (
            [
                i.lower().replace(" icon", "")
                for i in design_data.new_component_icons_elements.if_so_what_new_component_icons_elements_are_needed
            ]
            if design_data.new_component_icons_elements.does_new_component_need_icons_elements
            else []
        ),
        "components": [
            {
                "name": i.library_component_name,
                "usage": i.library_component_usage_reason,
            }
            for i in design_data.use_library_components
        ],
    }
    return {"component_task": component_task}
