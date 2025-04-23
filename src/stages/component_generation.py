# import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from src.util.langchain_schema import genState
from src.util.model_map import model_mapping

# os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]


def generate_component_stream(state: genState):
    comp_Prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert at writing React components.\nYour task is to write a new React component for a web app, according to the provided task details with best practices of React.\nThe React component you write can make use of Tailwind classes for styling.\nUtilize the library components and icons as much as you can.\n\nYou will write the full React component code, which should include all imports. Your generated code will be directly written to a .tsx React component file and used in production.",
            ),
            (
                "human",
                "<task_details>\n"
                "- COMPONENT NAME : {component_name}\n\n"
                "- COMPONENT DESCRIPTION :\n```\n"
                "{component_description}"
                "\n```\n\n"
                "- additional component suggestions :\n```\n"
                "{component_description_additional}"
                "{context}"
                "</task_details>\n"
                "\nWrite the full code for the new React web component, which uses Tailwind classes if needed (add tailwind dark: classes too if you can; backgrounds in dark: classes should be black), and, library components and icons, based on the provided design task.\n"
                "When using flexbox, use the `gap` property instead of `space-x`\n"
                "The full code of the new React component that you write will be written directly to a .tsx file inside the React project. Make sure all necessary imports are done, and that your full code is enclosed with ```tsx blocks.\n"
                "- Make sure you import provided components libraries and icons that are provided to you if you use them !\n"
                "- Tailwind classes should be written directly in the elements class tags (or className in case of React). DO NOT WRITE ANY CSS OUTSIDE OF CLASSES. DO NOT USE ANY <style> IN THE CODE ! CLASSES STYLING ONLY !\n"
                "- Do not use libraries or imports except what is provided in this task; otherwise it would crash the component because not installed. Do not import extra libraries besides what is provided above !\n"
                "- DO NOT HAVE ANY DYNAMIC DATA OR DATA PROPS ! Components are meant to be working as is without supplying any variable to them when importing them ! Only write a component that render directly with placeholders as data, component not supplied with any dynamic data.\n"
                "- DO NOT HAVE ANY DYNAMIC DATA OR DATA PROPS !\n- Use picsum.photos for placeholder images\n"
                "- DO NOT GENERATE SVG !\n"
                "- Only write the code for the component; Do not write extra code to import it! The code will directly be stored in an individual React .tsx file !\n"
                "- Very important : Your component should be exported as default !\n"
                "Write the React component code as the creative genius and React component genius you are - with good ui formatting.\n",
            ),
        ]
    )

    comp_model = ChatGoogleGenerativeAI(
        # model="gemini-2.5-pro-exp-03-25",
        model=model_mapping(state["model"]),
        api_key=state["gemini_api_key"],
        temperature=0.8,
        max_retries=2,
    )
    component_task = state["component_task"]
    input_ = {
        "component_name": component_task["name"],
        "component_description": component_task["description"]["user"],
        "component_description_additional": component_task["description"]["llm"],
        "context": state["context"],
    }

    code_generated = (comp_Prompt | comp_model).invoke(input_)

    history = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert at writing React components.\nYour task is to write a new React component for a web app, according to the provided task details with best practices of React.\nThe React component you write can make use of Tailwind classes for styling.\nUtilize the library components and icons as much as you can.\n\nYou will write the full React component code, which should include all imports. Your generated code will be directly written to a .tsx React component file and used in production.",
            ),
            (
                "human",
                "<task_details>\n"
                "- COMPONENT NAME : {component_name}\n\n"
                "- COMPONENT DESCRIPTION :\n```\n"
                "{component_description}"
                "\n```\n\n"
                "- additional component suggestions :\n```\n"
                "{component_description_additional}"
                "{context}"
                "</task_details>\n"
                "\nWrite the full code for the new React web component, which uses Tailwind classes if needed (add tailwind dark: classes too if you can; backgrounds in dark: classes should be black), and, library components and icons, based on the provided design task.\n"
                "When using flexbox, use the `gap` property instead of `space-x`\n"
                "The full code of the new React component that you write will be written directly to a .tsx file inside the React project. Make sure all necessary imports are done, and that your full code is enclosed with ```tsx blocks.\n"
                "- Make sure you import provided components libraries and icons that are provided to you if you use them !\n"
                "- Tailwind classes should be written directly in the elements class tags (or className in case of React). DO NOT WRITE ANY CSS OUTSIDE OF CLASSES. DO NOT USE ANY <style> IN THE CODE ! CLASSES STYLING ONLY !\n"
                "- Do not use libraries or imports except what is provided in this task; otherwise it would crash the component because not installed. Do not import extra libraries besides what is provided above !\n"
                "- DO NOT HAVE ANY DYNAMIC DATA OR DATA PROPS ! Components are meant to be working as is without supplying any variable to them when importing them ! Only write a component that render directly with placeholders as data, component not supplied with any dynamic data.\n"
                "- DO NOT HAVE ANY DYNAMIC DATA OR DATA PROPS !\n- Use picsum.photos for placeholder images\n"
                "- DO NOT GENERATE SVG !\n"
                "- Only write the code for the component; Do not write extra code to import it! The code will directly be stored in an individual React .tsx file !\n"
                "- Very important : Your component should be exported as default !\n"
                "Write the React component code as the creative genius and React component genius you are - with good ui formatting.\n",
            ),
            ("ai", "{code_generated}"),
        ]
    )

    history_input = {
        "component_name": component_task["name"],
        "component_description": component_task["description"]["user"],
        "component_description_additional": component_task["description"]["llm"],
        "context": state["context"],
        "code_generated": code_generated,
    }

    return {"history": history.invoke(history_input)}


def generate_component(state: genState):
    comp_Prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert at writing React components.\nYour task is to write a new React component for a web app, according to the provided task details with best practices of React.\nThe React component you write can make use of Tailwind classes for styling.\nUtilize the library components and icons as much as you can.\n\nYou will write the full React component code, which should include all imports. Your generated code will be directly written to a .tsx React component file and used in production.",
            ),
            (
                "human",
                "<task_details>\n"
                "- COMPONENT NAME : {component_name}\n\n"
                "- COMPONENT DESCRIPTION :\n```\n"
                "{component_description}"
                "\n```\n\n"
                "- additional component suggestions :\n```\n"
                "{component_description_additional}"
                "{context}"
                "</task_details>\n"
                "\nWrite the full code for the new React web component, which uses Tailwind classes if needed (add tailwind dark: classes too if you can; backgrounds in dark: classes should be black), and, library components and icons, based on the provided design task.\n"
                "When using flexbox, use the `gap` property instead of `space-x`\n"
                "The full code of the new React component that you write will be written directly to a .tsx file inside the React project. Make sure all necessary imports are done, and that your full code is enclosed with ```tsx blocks.\n"
                "- Make sure you import provided components libraries and icons that are provided to you if you use them !\n"
                "- Tailwind classes should be written directly in the elements class tags (or className in case of React). DO NOT WRITE ANY CSS OUTSIDE OF CLASSES. DO NOT USE ANY <style> IN THE CODE ! CLASSES STYLING ONLY !\n"
                "- Do not use libraries or imports except what is provided in this task; otherwise it would crash the component because not installed. Do not import extra libraries besides what is provided above !\n"
                "- DO NOT HAVE ANY DYNAMIC DATA OR DATA PROPS ! Components are meant to be working as is without supplying any variable to them when importing them ! Only write a component that render directly with placeholders as data, component not supplied with any dynamic data.\n"
                "- DO NOT HAVE ANY DYNAMIC DATA OR DATA PROPS !\n- Use picsum.photos for placeholder images\n"
                "- DO NOT GENERATE SVG !\n"
                "- Only write the code for the component; Do not write extra code to import it! The code will directly be stored in an individual React .tsx file !\n"
                "- Very important : Your component should be exported as default !\n"
                "Write the React component code as the creative genius and React component genius you are - with good ui formatting.\n",
            ),
        ]
    )

    comp_model = ChatGoogleGenerativeAI(
        # model="gemini-2.5-pro-exp-03-25",
        model=model_mapping(state["model"]),
        api_key=state["gemini_api_key"],
        temperature=0.8,
        max_retries=2,
    )
    component_task = state["component_task"]
    input_ = {
        "component_name": component_task["name"],
        "component_description": component_task["description"]["user"],
        "component_description_additional": component_task["description"]["llm"],
        "context": state["context"],
    }

    code_generated = (comp_Prompt | comp_model).invoke(input_)

    history = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert at writing React components.\nYour task is to write a new React component for a web app, according to the provided task details with best practices of React.\nThe React component you write can make use of Tailwind classes for styling.\nUtilize the library components and icons as much as you can.\n\nYou will write the full React component code, which should include all imports. Your generated code will be directly written to a .tsx React component file and used in production.",
            ),
            (
                "human",
                "<task_details>\n"
                "- COMPONENT NAME : {component_name}\n\n"
                "- COMPONENT DESCRIPTION :\n```\n"
                "{component_description}"
                "\n```\n\n"
                "- additional component suggestions :\n```\n"
                "{component_description_additional}"
                "{context}"
                "</task_details>\n"
                "\nWrite the full code for the new React web component, which uses Tailwind classes if needed (add tailwind dark: classes too if you can; backgrounds in dark: classes should be black), and, library components and icons, based on the provided design task.\n"
                "When using flexbox, use the `gap` property instead of `space-x`\n"
                "The full code of the new React component that you write will be written directly to a .tsx file inside the React project. Make sure all necessary imports are done, and that your full code is enclosed with ```tsx blocks.\n"
                "- Make sure you import provided components libraries and icons that are provided to you if you use them !\n"
                "- Tailwind classes should be written directly in the elements class tags (or className in case of React). DO NOT WRITE ANY CSS OUTSIDE OF CLASSES. DO NOT USE ANY <style> IN THE CODE ! CLASSES STYLING ONLY !\n"
                "- Do not use libraries or imports except what is provided in this task; otherwise it would crash the component because not installed. Do not import extra libraries besides what is provided above !\n"
                "- DO NOT HAVE ANY DYNAMIC DATA OR DATA PROPS ! Components are meant to be working as is without supplying any variable to them when importing them ! Only write a component that render directly with placeholders as data, component not supplied with any dynamic data.\n"
                "- DO NOT HAVE ANY DYNAMIC DATA OR DATA PROPS !\n- Use picsum.photos for placeholder images\n"
                "- DO NOT GENERATE SVG !\n"
                "- Only write the code for the component; Do not write extra code to import it! The code will directly be stored in an individual React .tsx file !\n"
                "- Very important : Your component should be exported as default !\n"
                "Write the React component code as the creative genius and React component genius you are - with good ui formatting.\n",
            ),
            ("ai", "{code_generated}"),
        ]
    )

    history_input = {
        "component_name": component_task["name"],
        "component_description": component_task["description"]["user"],
        "component_description_additional": component_task["description"]["llm"],
        "context": state["context"],
        "code_generated": code_generated,
    }
    chat_history = history.invoke(history_input)

    state["generatedCode"] = code_generated
    state["history"] = chat_history
    return state
