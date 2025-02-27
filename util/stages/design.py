import os
import json
from google import genai
from google.genai import types

from util.util.output_schema import ComponentSchema, ValidPromptSchema

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)


def prompt_validation(prompt):
    prompt_validation_config = types.GenerateContentConfig(
        temperature=0.2,
        systemInstruction="You are checking whether the user prompt is describing a web component.",
        responseMimeType="application/json",
        responseSchema=ValidPromptSchema,
    )

    validation_response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=prompt_validation_config,
        contents=prompt,
    )

    valid_check = eval(
        validation_response.text.replace("false", "False").replace("true", "True")
    )
    return valid_check["valid_prompt"]


def design_planning(prompt):
    with open("data/components/myds.json") as f:
        data = json.load(f)
    LIBRARY_COMPONENTS_MAP = [
        {"name": e["name"], "description": e["description"]} for e in data
    ]

    system_instruction = """Your task is to design a new React component for a web app, according to the user's request.\n` +
        `If you judge it is relevant to do so, you can specify pre-made library components to use in the component update.\n` +
        `You can also specify the use of icons if you see that the user's update request requires it."""

    generation_config = types.GenerateContentConfig(
        temperature=1,
        systemInstruction=system_instruction,
        responseMimeType="application/json",
        responseSchema=ComponentSchema,
    )

    contents = [
        types.Content(
            parts=[
                types.Part.from_text(
                    text="Multiple library components can be used while creating a new component update in order to help you do a better design job, faster.\n"
                    + "Be creative and utilize the limited set of components to build the component.\n\n"
                    + "AVAILABLE LIBRARY COMPONENTS:\n\n```\n"
                    + "\n".join(
                        [
                            f"{i['name']} : {i['description']}"
                            for i in LIBRARY_COMPONENTS_MAP
                        ]
                    )
                    + "\n```"
                    # + "\n\nWhen components are not available, output them in the `not_in_libraryComponent` field."
                    + "\n\nWhen suggesting icons, use common icon names used in Lucide icon library."
                    + "\nIMPORTANT:"
                    + "\nThe XIcon in the library refers to the twitter icon, use CrossIcon when the cross icon is needed."
                )
            ],
            role="model",
        ),
        types.Content(
            parts=[
                types.Part.from_text(
                    text=f"USER QUERY : \n```\n{prompt}\n```\n\nDesign the new React web component task for the user as the creative genius you are"
                )
            ],
            role="user",
        ),
    ]

    design_response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=generation_config,
        contents=contents,
    )

    design_data = eval(
        design_response.text.replace(
            '"does_new_component_need_icons_elements": true',
            '"does_new_component_need_icons_elements": True',
        )
        .replace(
            '"does_new_component_need_icons_elements": false',
            '"does_new_component_need_icons_elements": False',
        )
        .replace("null", "[]")
    )
    return design_data
