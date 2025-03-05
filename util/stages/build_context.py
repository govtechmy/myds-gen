import uuid
import pandas as pd
from util.util.rag import rag_icon, rag_component


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
        f"\n\n# full code examples of React components that use {comp_name} :\n"
        + "\n\n".join([f"```tsx\n{example.strip()}\n```" for example in comp_examples])
        + "\n\n"
        f"# API reference for {comp_name} :\n\n"
        + "\n".join(
            [f"## {c_name}\n\n{prop_md(c_prop)}" for c_name, c_prop in props.items()]
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


def parse_task(component_task):
    design_task = {
        "components": component_task["components"],
        "icons": component_task["icons"],
    }

    components_retrieved = [
            rag_component(i["name"]) for i in design_task["components"]
        ]
    
    components_retrieved = [x for i in components_retrieved for x in i] #flatten

    retrieved = {
        "icons": {
            "icons": [rag_icon(i) for i in design_task["icons"]],
            "import": "lucide-react",
        },
        "components": [i for n, i in enumerate(components_retrieved) if i not in components_retrieved[:n]]
    }

    flat_comp_list = [
        (i, x) for i, x in enumerate(retrieved["components"])
    ]

    total_suggestion = len(flat_comp_list)
    suggestion_comp_block = "\n\n".join(
        [
            f"Suggested library component ({i}/{total_suggestion}) : {x[1]['name']} - {x[1]['description']}\n"
            # + f"Suggested usage : {design_task['components'][x[0]]['usage']}\n\n\n"
            + f"# {x[1]['name']} can be imported into the new component like this:\n"
            + f"```tsx\n{x[1]['docs']['import'].strip()}\n```\n\n---\n\n# examples of how {x[1]['name']} can be used inside the new component:\n"
            + f"```tsx\n{x[1]['docs']['use']}```\n\n---"
            + example_block(
                x[1]["name"],
                x[1]["docs"]["examples"],
                x[1]["docs"]["props"],
            )
            for i, x in enumerate(flat_comp_list)
        ]
    )

    suggestion_comp_block = suggestion_comp_block + "\n\nSuggested library component usages: \n-" + "\n- ".join([f"{i['name']} - {i['usage']}" for i in design_task["components"]])
    if component_task["icons"]:
        example_icon = retrieved["icons"]["icons"][0]["retrieved"][0]
        suggestion_icon_block = (
            "Icon elements can optionally be used when making the React component.\n\n---\n\n"
            + "# example: importing icons in the component (only import the ones you need) :\n\n```tsx\nimport { "
            + " , ".join(
                [" , ".join(x["retrieved"]) for x in retrieved["icons"]["icons"]]
            )
            + " } from @govtechmy/myds-react/icon\n```\n\n# example: using an icon inside the component :\n\n```tsx\n"
            + f'<{example_icon} className="h-4 w-4" />\n```\n\n---\n\n\n'
            + "Here are some available icons that might be relevant to the component you are making. You can choose from them if relevant :\n\n```\n"
            + "\n".join(
                [f"- {i}" for x in retrieved["icons"]["icons"] for i in x["retrieved"]]
            )
            + "\n```"
        )
    else:
        suggestion_icon_block = ""
    return suggestion_comp_block, suggestion_icon_block


def generate(prompt, design_data, wireframe):
    component_task = gen_comp_task(prompt, design_data)
    suggestion_comp_block, suggestion_icon_block = parse_task(component_task)

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

    build_context = f"""Library components to be used while making the new React component

    {suggestion_comp_block}

    {suggestion_icon_block}

    {design_block}

    # Component Wireframe:

    {wireframe}

    Adhere to the wireframe when creating the component!
    """

    return component_task, build_context
