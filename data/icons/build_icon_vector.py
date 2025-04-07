import pandas as pd
import os
import re
import argparse
from google import genai

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]


def get_embeddings(s):
    client = genai.Client(api_key=GEMINI_API_KEY)
    result = client.models.embed_content(model="text-embedding-004", contents=s)
    return result.embeddings[0].values


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

    df = pd.DataFrame(icon_names, columns=["icon_name"])
    df["vector"] = df["icon_name"].apply(get_embeddings)
    df.to_parquet("data/icons/icon_vector.pq")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mydspath", type=str)
    args = parser.parse_args()
    icon_path = os.path.join(args.mydspath, "packages/react/src/icons")
    main(file_path=icon_path)
