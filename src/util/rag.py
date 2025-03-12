import os
import json
import numpy as np
import pandas as pd
from google import genai

DEP_TYPE = os.getenv("DEP_TYPE")
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

if DEP_TYPE == "serverless":
    import requests
    from io import BytesIO

    MYDS_JSON = os.environ["MYDS_JSON"]
    COMPONENT_DB = os.environ["COMPONENT_DB"]
    ICON_DB = os.environ["ICON_DB"]


def fake_rag_component(component_name):
    if DEP_TYPE == "serverless":
        response = requests.get(MYDS_JSON)
        data = response.json()
    else:
        with open("data/components/myds.json") as f:
            data = json.load(f)
    return [i for i in data if component_name.lower() in i["name"].lower()]


def get_embeddings(s):
    client = genai.Client(api_key=GEMINI_API_KEY)

    result = client.models.embed_content(model="text-embedding-004", contents=s)
    return result.embeddings[0].values


def rag_icon(icon_name):
    if DEP_TYPE == "serverless":
        response = requests.get(ICON_DB)
        df = pd.read_parquet(BytesIO(response.content))
    else:
        df = pd.read_parquet("data/icons/icon_vector.pq")
    query_embedding = get_embeddings(icon_name)
    top_ten_match = np.argsort(np.dot(np.stack(df["vector"]), query_embedding))[-10:][
        ::-1
    ]
    # print(results)
    return {
        "icon": icon_name,
        "retrieved": [df.iloc[i]["icon_name"] for i in top_ten_match],
    }


def rag_component(component_name):
    if DEP_TYPE == "serverless":
        response = requests.get(COMPONENT_DB)
        df = pd.read_parquet(BytesIO(response.content))
    else:
        df = pd.read_parquet("data/components/component_vector.pq")
    query_embedding = get_embeddings(component_name)
    top_2_match = np.argsort(np.dot(np.stack(df["vector"]), query_embedding))[-2:][::-1]
    top2retrieved = [df.iloc[i]["component_name"] for i in top_2_match]
    top2retrieved_comps = [x for i in top2retrieved for x in fake_rag_component(i)]

    return top2retrieved_comps
