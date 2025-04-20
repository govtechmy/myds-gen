# import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from src.util.output_schema import (
    ComponentSchema,
    ValidPromptSchema,
    WireframeSchema,
    PromptImproved,
)

from src.util.langchain_schema import designState, learnState
# os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]


def validate(state: designState):
    validation_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are checking whether the user prompt is describing a web component. If the prompt is describing a webpage it is not a web component.",
            ),
            ("human", "{user_prompt}"),
        ]
    )

    valid_check = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        api_key=state["gemini_api_key"],
        temperature=0.2,
        max_retries=2,
    ).with_structured_output(ValidPromptSchema)
    out = (validation_prompt | valid_check).invoke(
        {"user_prompt": state["user_prompt"]}
    )
    return {"valid": out.valid_prompt}


def enhance(state: learnState):
    enhancement_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a senior UIUX Designer for designing developments of web components in the React framework.",
            ),
            (
                "human",
                """Improve the user's request in `<original prompt>` to be more descriptive by including the shadcn components that will be needed. Do not mention the library in your output. However do not recommend the `Card`, `Avatar`, `Typography` and `Sheet` component as they are currently unavailable.

        <original_prompt>
            {user_prompt}
        </original_prompt>""",
            ),
        ]
    )

    enhancement_model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        api_key=state["gemini_api_key"],
        temperature=1,
        max_retries=2,
    ).with_structured_output(PromptImproved)
    return {
        "enhanced_prompt": (enhancement_prompt | enhancement_model).invoke(
            {"user_prompt": state["user_prompt"]}
        )
    }


def plan(state: learnState):
    comp_include_ = "\n".join(
        [f"{i['name']} : {i['description']}" for i in state["comp_include"]]
    )
    plan_Prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Your task is to design a new React component for a web app, according to the user's request.\nSpecify the pre-made library components to use in the task.\nYou must also specify the use of icons if you see that the task requires it.",
            ),
            (
                "human",
                "Multiple library components can be used while creating a new component update in order to help you do a better design job, faster.\n"
                "Be creative and only utilize the limited set of components to build the component.\n\n"
                "AVAILABLE LIBRARY COMPONENTS:\n\n"
                "{comp_include}"
                "\n\nList all icons that will be needed in the component, use common icon names used in Lucide icon library."
                "\n**IMPORTANT:**"
                "\n**Use CrossIcon when the cross or closing or cancel icon is needed.**"
                "\n**Card, Avatar, Typography and Sheet component is not available.**",
            ),
            (
                "human",
                "USER QUERY : \n```\n{enhanced_request}\n```\n\nDesign the new React web component task as the creative genius you are",
            ),
        ]
    )

    prompt_model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        api_key=state["gemini_api_key"],
        temperature=0.6,
        max_retries=2,
    ).with_structured_output(ComponentSchema)
    return {
        "design_plan": (plan_Prompt | prompt_model).invoke(
            {
                "comp_include": comp_include_,
                "enhanced_request": state["enhanced_prompt"].improved_request,
            }
        )
    }


def wireframe(state: learnState):
    wireframe_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert senior UIUX Designer.\nYour task is to design the wireframe of new React component for a web app, according to the provided task details.\nSpecify the library components and the icons in the wireframe diagram.",
            ),
            (
                "human",
                "- COMPONENT NAME : {component_name}\n\n"
                "- COMPONENT DESCRIPTION :\n```\n"
                "{component_description}"
                "\n```\n\n"
                "- additional component suggestions :\n```\n"
                "{component_description_additional}"
                "\n```"
                "\n\nCreate detailed wireframe using ASCII based on the provided design task and available library components.\n\n"
                "**Available library components**\n- "
                "{library_comp}"
                "{icon_elem}"
                "\n\nOutput the generated wireframe in a ```ascii ``` block\n"
                "You should make all assumptioms.\n"
                "Specify the library components and the icons in the detailed wireframe diagram.\n"
                "The detailed wireframe must look clean and professional as the creative genius you are.",
            ),
        ]
    )

    wireframe_model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        api_key=state["gemini_api_key"],
        temperature=0.8,
        max_retries=2,
    ).with_structured_output(WireframeSchema)
    component_task = state["component_task"]
    input_ = {
        "component_name": component_task["name"],
        "component_description": component_task["description"]["user"],
        "component_description_additional": component_task["description"]["llm"],
        "library_comp": "\n- ".join([i["name"] for i in component_task["components"]]),
        "icon_elem": ("**Icon Elements**\n- " if component_task["icons"] else "")
        + (
            "\n- ".join([i for i in component_task["icons"]])
            if component_task["icons"]
            else ""
        ),
    }
    return {"wireframe": (wireframe_prompt | wireframe_model).invoke(input_)}
