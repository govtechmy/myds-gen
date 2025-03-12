import os
import uuid
import pandas as pd
from src.util.rag import rag_icon, rag_component

DEP_TYPE = os.getenv("DEP_TYPE")

if DEP_TYPE == "serverless":
    import requests

    DESIGN_DOC = os.environ["DESIGN_DOC"]
    COLOR_DOC = os.environ["COLOR_DOC"]

# ----------------
# processing markdown tables and code examples
def prop_md(prop_dict):
    base_df = pd.DataFrame(
        columns=["description", "type", "default", "typeDescription"]
    )
    prop_df = pd.DataFrame.from_dict(prop_dict).T
    base_df = pd.concat([base_df, prop_df]).fillna("-")
    return base_df.to_markdown(tablefmt="github")


def example_block(comp_name, comp_examples, props):
    return (
        f"\n\n## full code examples of React components that use `{comp_name}` :\n"
        + "\n\n".join([f"```tsx\n{example.strip()}\n```" for example in comp_examples])
        + "\n\n"
        f"## API reference for `{comp_name}` :\n"
        + "\n".join(
            [f"\n### {c_name}\n\n{prop_md(c_prop)}" for c_name, c_prop in props.items()]
        )
    )


# ----------------


def gen_comp_task(prompt, design_data):
    component_task = {
        "name": f"{design_data['new_component_name']}_{uuid.uuid4()}",
        "description": {
            "user": prompt,
            "llm": design_data["new_component_description"],
        },
        "icons": (
            [
                i.lower().replace(" icon", "")
                for i in design_data["new_component_icons_elements"][
                    "if_so_what_new_component_icons_elements_are_needed"
                ]
            ]
            if design_data["new_component_icons_elements"][
                "does_new_component_need_icons_elements"
            ]
            else []
        ),
        "components": [
            {
                "name": i["library_component_name"],
                "usage": i["library_component_usage_reason"],
            }
            for i in design_data["use_library_components"]
        ],
    }
    return component_task


def gen_comp_task_iter(prompt, design_data, current_component_task):
    update = {
        "update_prompt": prompt,
        "update_description": design_data["description_of_update"],
        "icons": (
            [
                i.lower().replace(" icon", "")
                for i in design_data["new_component_icons_elements"][
                    "if_so_what_new_component_icons_elements_are_needed"
                ]
            ]
            if design_data["new_component_icons_elements"][
                "does_new_component_need_icons_elements"
            ]
            else []
        ),
        "components": (
            [
                {
                    "name": i["library_component_name"],
                    "usage": i["library_component_usage_reason"],
                }
                for i in design_data["new_library_components"][
                    "if_so_what_library_components_are_needed"
                ]
            ]
            if design_data["new_library_components"][
                "does_update_need_new_library_components"
            ]
            else []
        ),
        "wireframe": design_data["wireframe_need_to_be_updated"],
    }
    component_task = current_component_task
    component_task["update"] = update
    return component_task


def parse_task(component_task):
    design_task = {
        "components": component_task["components"],
        "icons": component_task["icons"],
    }

    components_retrieved = [rag_component(i["name"]) for i in design_task["components"]]

    components_retrieved = [x for i in components_retrieved for x in i]  # flatten

    retrieved = {
        "icons": [rag_icon(i) for i in design_task["icons"]],
        "components": [
            i
            for n, i in enumerate(components_retrieved)
            if i not in components_retrieved[:n]
        ],
    }

    flat_comp_list = [(i, x) for i, x in enumerate(retrieved["components"])]

    total_suggestion = len(flat_comp_list)
    suggestion_comp_block_ = "\n\n".join(
        [
            f"# Suggested library component ({i}/{total_suggestion}) : {x[1]['name']}\n- {x[1]['description']}\n"
            # + f"Suggested usage : {design_task['components'][x[0]]['usage']}\n\n\n"
            + f"## {x[1]['name']} can be imported into the new component like this:\n"
            + f"```tsx\n{x[1]['docs']['import'].strip()}\n```\n\n---\n\n## examples of how `{x[1]['name']}` can be used inside the new component:\n"
            + f"```tsx\n{x[1]['docs']['use']}\n```\n"
            + example_block(
                x[1]["name"],
                x[1]["docs"]["examples"],
                x[1]["docs"]["props"],
            )
            for i, x in enumerate(flat_comp_list)
        ]
    )

    suggestion_comp_block = (
        "# Suggested library component usages: \n- "
        + "\n- ".join(
            [f"{i['name']} - {i['usage']}" for i in design_task["components"]]
        )
        + "\n\n"
        + suggestion_comp_block_
    )
    if component_task["icons"]:
        example_icon = retrieved["icons"][0]["retrieved"][0]
        suggestion_icon_block = (
            "Icon elements can optionally be used when making the React component.\n\n---\n\n"
            + "# example: importing icons in the component (only import the ones you need) :\n\n```tsx\nimport { "
            + " , ".join([" , ".join(x["retrieved"]) for x in retrieved["icons"]])
            + " } from @govtechmy/myds-react/icon\n```\n\n# example: using an icon inside the component :\n\n```tsx\n"
            + f'<{example_icon} className="h-4 w-4" />\n```\n\n---\n\n\n'
            + "Here are some available icons that might be relevant to the component you are making. You can choose from them if relevant :\n\n```\n"
            + "\n".join([f"- {i}" for x in retrieved["icons"] for i in x["retrieved"]])
            + "\n```"
        )
    else:
        suggestion_icon_block = ""
    return suggestion_comp_block, suggestion_icon_block


def generate(component_task, wireframe):
    # component_task = gen_comp_task(prompt, design_data)
    suggestion_comp_block, suggestion_icon_block = parse_task(component_task)

    if DEP_TYPE == "serverless":
        response = requests.get(DESIGN_DOC)
        design_text = response.text
    else:
        with (
            open("data/foundation/design_doc_min.md") as design_raw
        ):  # a distilled version of https://myds.vercel.app/en/docs/design foundation tabs
            design_text = design_raw.readlines()

    design_text = "".join(design_text)
    
    if DEP_TYPE == "serverless":
        response = requests.get(COLOR_DOC)
        colour_text = response.text
    else:
        with (
            open("data/foundation/colour.md") as design_colour
        ):  # extracted from https://github.com/govtechmy/myds/tree/main/packages/style/styles/theme
            colour_text = design_colour.readlines()

    colour_text = "".join(colour_text)

    design_text = design_text + "\n\n" + colour_text

    design_block = f"**When creating components you are to adhere to the Malaysian Design System**\nKeeep in mind components created should have neat and organized layout !\n\n{design_text}"

    build_context = f"""# Wireframe Design of the component

**Adhere fully to the wireframe, crafted by an expert UIUX Designer when building the component !**

{wireframe}

---
**Library components to be used while making the new React component.**

{suggestion_comp_block}

{suggestion_icon_block}

{design_block}
"""

    return build_context


def parse_task_iter(component_task):
    design_task = {
        "components": component_task["update"]["components"],
        "icons": component_task["update"]["icons"],
    }

    if design_task["components"]:
        components_retrieved = [
            rag_component(i["name"]) for i in design_task["components"]
        ]

        components_retrieved = [x for i in components_retrieved for x in i]  # flatten
    else:
        components_retrieved = None

    retrieved = {
        "icons": [rag_icon(i) for i in design_task["icons"]]
        if design_task["icons"]
        else [],
        "components": [
            i
            for n, i in enumerate(components_retrieved)
            if i not in components_retrieved[:n]
        ]
        if components_retrieved
        else [],
    }

    if retrieved["components"]:
        flat_comp_list = [(i, x) for i, x in enumerate(retrieved["components"])]

        total_suggestion = len(flat_comp_list)
        suggestion_comp_block_ = "\n\n".join(
            [
                f"# Suggested library component ({i}/{total_suggestion}) : {x[1]['name']}\n- {x[1]['description']}\n"
                # + f"Suggested usage : {design_task['components'][x[0]]['usage']}\n\n\n"
                + f"## {x[1]['name']} can be imported into the new component like this:\n"
                + f"```tsx\n{x[1]['docs']['import'].strip()}\n```\n\n---\n\n## examples of how `{x[1]['name']}` can be used inside the new component:\n"
                + f"```tsx\n{x[1]['docs']['use']}\n```\n"
                + example_block(
                    x[1]["name"],
                    x[1]["docs"]["examples"],
                    x[1]["docs"]["props"],
                )
                for i, x in enumerate(flat_comp_list)
            ]
        )

        suggestion_comp_block = (
            "# Suggested library component usages: \n- "
            + "\n- ".join(
                [f"{i['name']} - {i['usage']}" for i in design_task["components"]]
            )
            + "\n\n"
            + suggestion_comp_block_
        )
    else:
        suggestion_comp_block = ""

    if component_task["update"]["icons"]:
        example_icon = retrieved["icons"][0]["retrieved"][0]
        suggestion_icon_block = (
            "Icon elements can optionally be used when making the React component.\n\n---\n\n"
            + "# example: importing icons in the component (only import the ones you need) :\n\n```tsx\nimport { "
            + " , ".join([" , ".join(x["retrieved"]) for x in retrieved["icons"]])
            + " } from @govtechmy/myds-react/icon\n```\n\n# example: using an icon inside the component :\n\n```tsx\n"
            + f'<{example_icon} className="h-4 w-4" />\n```\n\n---\n\n\n'
            + "Here are some available icons that might be relevant to the component you are making. You can choose from them if relevant :\n\n```\n"
            + "\n".join([f"- {i}" for x in retrieved["icons"] for i in x["retrieved"]])
            + "\n```"
        )
    else:
        suggestion_icon_block = ""

    return suggestion_comp_block, suggestion_icon_block


def generate_iter(component_task, wireframe):
    # component_task = gen_comp_task(prompt, design_data)
    suggestion_comp_block, suggestion_icon_block = parse_task_iter(component_task)

    with (
        open("data/foundation/design_doc_min.md") as design_raw
    ):  # a distilled version of https://myds.vercel.app/en/docs/design foundation tabs
        design_text = design_raw.readlines()

    design_text = "".join(design_text)

    with (
        open("data/foundation/colour.md") as design_colour
    ):  # extracted from https://github.com/govtechmy/myds/tree/main/packages/style/styles/theme
        colour_text = design_colour.readlines()

    colour_text = "".join(colour_text)

    design_text = design_text + "\n\n" + colour_text

    design_block = f"**When creating components you are to adhere to the Malaysian Design System**\nKeeep in mind components created should have neat and organized layout !\n\n{design_text}"

    build_context = f"""# Wireframe Design of the component

**Adhere fully to the wireframe, crafted by an expert UIUX Designer when updating the component !**

{wireframe}

---
{"**Library components to be used while making the new React component.**" + chr(10) + chr(10) if suggestion_comp_block else ""}{suggestion_comp_block}{chr(10) + chr(10) if suggestion_comp_block else ""}{suggestion_icon_block}{chr(10) + chr(10) if suggestion_icon_block else ""}
{design_block}
"""

    return build_context
