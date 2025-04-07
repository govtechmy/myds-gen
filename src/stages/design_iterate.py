import os
import json
from google import genai
from google.genai import types
from src.util.output_schema import ComponentIterateSchema, WireframeSchema, PromptImprovedIter
from src.util.rag import rag_component

DEP_TYPE = os.getenv("DEP_TYPE")
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)

# if DEP_TYPE == "serverless":
#     import requests

#     MYDS_JSON = os.environ["MYDS_JSON"]

def prompt_improve(prompt, current_code):
    system_instruction = "You are a senior UIUX Designer for designing developments of web components in the React framework."

    generation_config = types.GenerateContentConfig(
        temperature=1,
        systemInstruction=system_instruction,
        responseMimeType="application/json",
        responseSchema=PromptImprovedIter,
    )
    contents = [
        types.Content(
            parts=[
                types.Part.from_text(
                    text="The user is trying to create an update request for the component in `<original code>`. Improve the user's request in `<original prompt>` to be more descriptive by including the additional shadcn components that will be needed. Do not mention the library in your output. However do not recommend the `Card` component as it is currently unavailable."
                    +"<original code>\n"
                    + "```tsx\n"
                    + current_code
                    + "\n```\n"
                    +"<original code/>\n"
                    +"<original prompt>\n"
                    + prompt
                    +"\n<original prompt/>"
                )
            ],
            role="user"
        )
    ]
    prompt_improve_response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        config=generation_config,
        contents=contents,
    )
    prompt_improve_data = json.loads(prompt_improve_response.text)
    return prompt_improve_data

def design_update(prompt, current_code, current_wireframe, current_component_task):
    # if DEP_TYPE == "serverless":
    #     response = requests.get(MYDS_JSON)
    #     data = response.json()
    # else:
    #     with open("data/components/myds.json") as f:
    #         data = json.load(f)
    # LIBRARY_COMPONENTS_MAP = [
    #     {"name": e["name"], "description": e["description"]} for e in data
    # ]

    new_prompt = prompt_improve(prompt, current_code)

    prompt = new_prompt["improved_request"]
    if new_prompt["additional_components"]:
        comp_include = [rag_component(f"{i['library_component_name']} - {i['library_component_usage_reason']}") for i in new_prompt["additional_components"]]
        comp_include = [x for i in comp_include for x in i]
        comp_include = [
                i
                for n, i in enumerate(comp_include)
                if i not in comp_include[:n]
            ]
        comp_include = "\n".join(
                        [
                            f"`{i['name']}` : {i['description']}"
                            for i in comp_include
                        ]
                    )
    else:
        comp_include = ""
    system_instruction = """Your task is to modify a React component for a web app, according to the user's request.
If you judge it is relevant to do so, you can specify pre-made library components to use in the component update.
You must also specify the use of icons if you see that the user's update request requires it."""

    generation_config = types.GenerateContentConfig(
        temperature=0.6,
        systemInstruction=system_instruction,
        responseMimeType="application/json",
        responseSchema=ComponentIterateSchema,
    )

    contents = [
        types.Content(
            parts=[
                types.Part.from_text(
                    text="Multiple library components can be used while creating a new component update in order to help you do a better design job, faster.\n"
                    + "Be creative and only utilize the limited set of components to update the component.\n\n"
                    + "AVAILABLE LIBRARY COMPONENTS:\n\n"
                    + comp_include
                    + "\n\nWhen suggesting icons, use common icon names used in Lucide icon library."
                    + "\n**IMPORTANT:**"
                    + "\n**Use CrossIcon when the cross or closing or cancel icon is needed.**"
                    + "\n**Card component is not available.**"
                )
            ],
            role="user",
        ),
        types.Content(
            parts=[
                types.Part.from_text(
                    text=f"- COMPONENT NAME : {current_component_task['name']}\n\n"
                    + "- COMPONENT DESCRIPTION :\n```\n"
                    + current_component_task["description"]["user"]
                    + "\n```\n\n"
                    + "- additional component suggestions :\n```\n"
                    + current_component_task["description"]["llm"]
                    + "\n```\n\n"
                    + "- NEW COMPONENT UPDATES QUERY :\n```\n"
                    + prompt
                    + "\n```\n\n"
                    + "- current component code :\n"
                    + current_code
                    + "\n\n"
                    + "- current wireframe :\n"
                    + current_wireframe
                    + "\n\n"
                    + "Design the React web component updates for the user, and determine if the wireframe should be updated.\n"
                    + "When web components are added or removed, the wireframe should be updated\n"
                    # + "Plan a general plan for Gemini-2.0-flash to perform the update on the next step, split into subtasks if you deem it necessary"
                )
            ],
            role="user",
        ),
    ]
    # print("\n".join([x.text for i in contents for x in i.parts]))
    design_response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        config=generation_config,
        contents=contents,
    )
    design_data = json.loads(design_response.text)
    return new_prompt['improved_request'], design_data


def design_layout(component_task, current_wireframe):
    system_instruction = """You are an expert senior UIUX Designer.\nYour task is to update the wireframe of new React component for a web app, according to the provided task details.\nSpecify the library components and the icons in the wireframe diagram."""

    generation_config = types.GenerateContentConfig(
        temperature=0.2,
        systemInstruction=system_instruction,
        responseMimeType="application/json",
        responseSchema=WireframeSchema,
    )

    design_response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        config=generation_config,
        contents=[
            f"- COMPONENT NAME : {component_task['name']}\n\n"
            + "- COMPONENT DESCRIPTION :\n```\n"
            + component_task["description"]["user"]
            + "\n```\n\n"
            + "- additional component suggestions :\n```\n"
            + component_task["description"]["llm"]
            + "\n```\n\n"
            + "- COMPONENT UPDATE QUERY :\n```\n"
            + component_task["update"]["update_prompt"]
            + "\n```\n\n"
            + "- additional component update suggestions :\n```\n"
            + component_task["update"]["update_description"]
            + "\n```\n\n"
            + "- current wireframe :\n"
            + current_wireframe
            + "\n\n"
            + "\n\nUpdate the given ASCII wireframe based on the updated design task and available library components.\n"
            + "The updated wireframe should onlu include changes described by the new updates query\n\n"
            + "Retain as much of the original wireframe as possible !\n"
            + "ONLY ADD OR REMOVE ITEMS THAT WERE MENTIONED IN THE UPDATE QUERIES !\n\n"
            + "**Library components to be included !**\n- "
            + "\n- ".join([i["name"] for i in component_task["update"]["components"]])
            + ("**Icon Elements**\n- " if component_task["update"]["icons"] else "")
            + (
                "\n- ".join([i for i in component_task["update"]["icons"]])
                if component_task["update"]["icons"]
                else ""
            )
            + "\n\nOutput the generated wireframe in a ```ascii ``` block"
            # + "Specify the library components and the icons in the detailed wireframe diagram.\n"
            + "The detailed wireframe must look clean and professional."
        ],
    )
    design_response = json.loads(design_response.text)["ascii_wireframe"]
    return design_response
