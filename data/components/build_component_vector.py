import pandas as pd
import json
import os
from google import genai

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]


def get_embeddings(s):
    client = genai.Client(api_key=GEMINI_API_KEY)
    result = client.models.embed_content(model="text-embedding-004", contents=s)
    return result.embeddings[0].values


def main():
    ##hardcoded for now
    with open("data/components/myds.json") as f:
        data = json.load(f)
    
    components = [[i["name"], i["name"]+ " - " + i["description"]]  for i in data]

    df = pd.DataFrame(components, columns=["component_name","description"])
    df["vector"] = df["description"].apply(get_embeddings)
    df.to_parquet("data/components/component_vector.pq")


if __name__ == "__main__":
    main()
