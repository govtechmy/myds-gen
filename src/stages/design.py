import os
import json
from google import genai
from google.genai import types

from src.util.output_schema import ComponentSchema, ValidPromptSchema, WireframeSchema, PromptImproved
from src.util.rag import rag_component

DEP_TYPE = os.getenv("DEP_TYPE")
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)

# if DEP_TYPE == "serverless":
#     import requests

#     MYDS_JSON = os.environ["MYDS_JSON"]


def prompt_validation(prompt):
    prompt_validation_config = types.GenerateContentConfig(
        temperature=0.2,
        systemInstruction="You are checking whether the user prompt is describing a web component. If the prompt is describing a webpage it is not a web component.",
        responseMimeType="application/json",
        responseSchema=ValidPromptSchema,
    )

    validation_response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=prompt_validation_config,
        contents=prompt,
    )

    valid_check = json.loads(validation_response.text)
    return valid_check["valid_prompt"]

def prompt_improve(prompt):
    system_instruction = "You are a senior UIUX Designer for designing developments of web components in the React framework."

    generation_config = types.GenerateContentConfig(
        temperature=1,
        systemInstruction=system_instruction,
        responseMimeType="application/json",
        responseSchema=PromptImproved,
    )

    improve_response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        config=generation_config,
        # contents=[prompt]
        contents=[f"""Improve the user's request in `<original prompt>` to be more descriptive by including the shadcn components that will be needed. Do not mention the library in your output. However do not recommend the `Card` component as it is currently unavailable.

    <original_prompt>
        {prompt}
    </original_prompt>"""]
    )

    improve_data = json.loads(improve_response.text)
    return improve_data

def design_planning(prompt):
    # if DEP_TYPE == "serverless":
    #     response = requests.get(MYDS_JSON)
    #     data = response.json()
    # else:
    #     with open("data/components/myds.json") as f:
    #         data = json.load(f)
    # LIBRARY_COMPONENTS_MAP = [
    #     {"name": e["name"], "description": e["description"]} for e in data
    # ]

    new_prompt = prompt_improve(prompt)

    comp_include = [rag_component(f"{i['library_component_name']} - {i['library_component_usage_reason']}") for i in new_prompt["components"]]
    comp_include = [x for i in comp_include for x in i]
    comp_include = [
            i
            for n, i in enumerate(comp_include)
            if i not in comp_include[:n]
        ]

    system_instruction = """Your task is to design a new React component for a web app, according to the user's request.\nSpecify the pre-made library components to use in the task.\nYou must also specify the use of icons if you see that the task requires it."""

    generation_config = types.GenerateContentConfig(
        temperature=0.6,
        systemInstruction=system_instruction,
        responseMimeType="application/json",
        responseSchema=ComponentSchema,
    )

    contents = [
        types.Content(
            parts=[
                types.Part.from_text(
                    text="Multiple library components can be used while creating a new component update in order to help you do a better design job, faster.\n"
                    + "Be creative and only utilize the limited set of components to build the component.\n\n"
                    + "AVAILABLE LIBRARY COMPONENTS:\n\n"
                    + "\n".join(
                        [
                            f"{i['name']} : {i['description']}"
                            for i in comp_include
                        ]
                    )
                    # + "\n```"
                    # + "\n\nWhen components are not available, output them in the `not_in_libraryComponent` field."
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
                    text=f"USER QUERY : \n```\n{new_prompt['improved_request']}\n```\n\nDesign the new React web component task for the user as the creative genius you are"
                )
            ],
            role="user",
        ),
    ]

    design_response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        config=generation_config,
        contents=contents,
    )

    design_data = json.loads(design_response.text)
    return new_prompt['improved_request'], design_data


def design_layout(component_task):
    # component_task = gen_comp_task(prompt, design_data)
    system_instruction = """You are an expert senior UIUX Designer.\nYour task is to design the wireframe of new React component for a web app, according to the provided task details.\nSpecify the library components and the icons in the wireframe diagram."""

    generation_config = types.GenerateContentConfig(
        temperature=0.8,
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
            + "\n```"
            + "\n\nCreate detailed wireframe using ASCII based on the provided design task and available library components.\n\n"
            + "**Available library components**\n- "
            + "\n- ".join([i["name"] for i in component_task["components"]])
            + ("**Icon Elements**\n- " if component_task["icons"] else "")
            + (
                "\n- ".join([i for i in component_task["icons"]])
                if component_task["icons"]
                else ""
            )
            + "\n\nOutput the generated wireframe in a ```ascii ``` block\n"
            + "You should make all assumptioms.\n"
            + "Specify the library components and the icons in the detailed wireframe diagram.\n"
            + "The detailed wireframe must look clean and professional as the creative genius you are."
        ],
    )
    design_response = json.loads(design_response.text)["ascii_wireframe"]
    return design_response
