import inspect
import re
import os
import json
import argparse
import build_component_vector


def prop_proc(s):
    a = ":"
    b = ""
    return f'"{s.group(0).strip().replace(a, b)}":'


def extract_comp_dict(mydspath, filename):
    with open(
        os.path.join(mydspath, f"apps/docs/content/docs/develop/(components)/{filename}.mdx")
    ) as f:
        data = f.readlines()
    full_text = "".join(data)
    name = re.findall(r"title: ([^\n]*)", full_text)[0]
    description = re.findall(r"description: ([^\n]*)", full_text)[0]
    test_split = full_text.split("\n## ")[1:]

    if filename == "pagination":
        usage = [i for i in test_split if i.split("\n")[0] == "Simple Usage"]
    else:
        usage = [i for i in test_split if i.split("\n")[0] == "Usage"]
    props = [i for i in test_split if i.split("\n")[0] == "Props"][0]

    usage_doc = [i for i in re.findall(r"```ts[\s\S]+?\n([\S\s]+?)\n```*", usage[0])]

    try:
        examples = [
            i
            for i in test_split
            if i.split("\n")[0] not in ["Props", "Usage", "Simple Usage"]
        ]
        examples_doc = re.findall(r"```tsx\s?\n([\S\s]+?)```*", examples[0])
        examples_doc = [
            inspect.cleandoc(ix).replace("\n", "\n\t\t") for ix in examples_doc
        ]
        examples_doc = [
            usage_doc[0]
            + "\n"
            + f"export default function component() {{\n\treturn ({i}\n\t);\n}}"
            for i in examples_doc
        ]
    except IndexError:
        examples_doc = []

    if filename == "pagination":
        examples_doc = [examples_doc[0]]

    prop_dict = {
        i.split("\n")[0].strip(): re.findall(
            r"<TypeTable\s*?type={{([\S\s]+?)}}\s*?\/>", i
        )
        for i in props.split("###")[1:]
    }
    if filename == "theme-switch":
        prop_dict = {
            i: eval(
                "{"
                + re.sub(r"\s\s\w+:", prop_proc, y)
                .replace('"`', '"')
                .replace('`"', '"')
                .replace(
                    '"default": (\n        <pre>\n          <code>\n            {`[',
                    '"default": """[',
                )
                .replace("`}\n          </code>\n        </pre>\n      )", '"""')
                .replace("`", '"""')
                + "}"
            )
            for i, x in prop_dict.items()
            for y in x
        }
    else:
        prop_dict = {
            i: eval(
                "{"
                + re.sub(r"\s\s\w+:", prop_proc, y)
                .replace('"`', '"')
                .replace('`"', '"')
                + "}"
            )
            for i, x in prop_dict.items()
            for y in x
        }
    return {
        "name": name,
        "description": description,
        "docs": {
            "import": usage_doc[0],
            "anatomy": usage_doc[1].replace(
                "<AlertDialog>", '<AlertDialog variant="default">'
            ),  # force usage of variant param on alert dialog
            "props": prop_dict,
            "examples": examples_doc,
        },
    }


def generate_json(myds_path):
    myds_docs_json = []
    comp_files = [
        i
        for i in os.listdir(os.path.join(myds_path, "apps/docs/content/docs/develop/(components)"))
        if ".ms.mdx" not in i
    ]
    for component in comp_files:
        if component not in ["banner.mdx"]:
            myds_docs_json.append(extract_comp_dict(myds_path, component.split(".")[0]))

    with open("data/components/myds.json", "w") as f:
        json.dump(myds_docs_json, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mydspath", type=str)
    args = parser.parse_args()
    myds_path = args.mydspath
    generate_json(myds_path)

    build_component_vector.main()
