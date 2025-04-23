# import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from src.stages.build_context import gen_comp_task_iter_, parse_task_
from src.util.langchain_schema import genStateIter
from src.util.output_schema import ComponentIterateSchema, PromptImprovedIter
from src.util.rag import rag_component
from src.util.model_map import model_mapping

# os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]


def prompt_enhance_iter(state: genStateIter):
    design_prompt = state["history"].model_copy(deep=True)
    new_prompt = f"""The user is requesting an update to the component you generated.
    Based on the update request stated in <update_request>, list additional library components from shadcn that might be needed to perform the update in addtional_components field: 
    <update_request>
    {state["new_prompt"]}
    </update_request>. 
    
    <important>
    Improve my update request in `<update_request>` to be more descriptive.
    list additional library components needed in the `addtional_components` field of your outut!
    Do not mention the library in your output.
    However do not recommend the `Card` and `Sheet` component as these are currently unavailable.
    </important>
    """
    design_prompt.messages.append(HumanMessage(content=new_prompt))

    design_model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        api_key=state["gemini_api_key"],
        temperature=1,
        max_retries=2,
    ).with_structured_output(PromptImprovedIter)

    return {"enhance_prompt": design_model.invoke(design_prompt)}


def design_update(state: genStateIter):
    design_prompt = state["history"].model_copy(deep=True)
    new_enh_prompt = state["enhance_prompt"]

    prompt = new_enh_prompt.improved_request
    if new_enh_prompt.additional_components:
        comp_include = [
            rag_component(
                f"{i.library_component_name} - {i.library_component_usage_reason}",
                state["gemini_api_key"],
            )
            for i in new_enh_prompt.additional_components
        ]
        comp_include = [x for i in comp_include for x in i]
        comp_include = [
            i for n, i in enumerate(comp_include) if i not in comp_include[:n]
        ]

        comp_include = "\n".join(
            [f"`{i['name']}` : {i['description']}" for i in comp_include]
        )
    else:
        comp_include = ""

    new_design_prompt = f"""The user is requesting an update to the component you generated.
    Based on the update request stated in <update_request>, design the React web component updates for the user, and determine if the wireframe should be updated: 
    <update_request>
    {prompt}
    </update_request>. 
    
    <task_details>
    Plan the component update task, determine the pre-made library components to be used in the component update, based on the list of components provided in <library_component>.
    You must also specify the use of icons if you see that the user's update request requires it.
    When suggesting icons, use common icon names used in Lucide icon library. **Use CrossIcon when the cross or closing or cancel icon is needed.**
    When web components are added or removed, update the ascii_wireframe of the component to integrate the update requested.
    </task_details>

    <library_component>
    {"ADDITIONAL LIBRARY COMPONENTS:" if comp_include else "no additional library components needed"}
    {comp_include}
    </library_component>
    """
    design_prompt.messages.append(HumanMessage(content=new_design_prompt))

    design_model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        api_key=state["gemini_api_key"],
        temperature=0.4,
        max_retries=2,
    ).with_structured_output(ComponentIterateSchema)

    return {"design_plan": design_model.invoke(design_prompt)}


def generate_component_iter_stream(state: genStateIter):
    comp_Prompt = state["history"].model_copy(deep=True)
    new_enh_prompt = state["enhance_prompt"]
    design_plan = state["design_plan"]
    prompt = new_enh_prompt.improved_request

    parsed_plan = gen_comp_task_iter_(prompt, design_plan)

    suggestion_comp_block, suggestion_icon_block, suggestion_wireframe_block = (
        parse_task_(parsed_plan, state["gemini_api_key"])
    )

    new_prompt = f"""The user is requesting an update to the component you generated.
    Update the component based on <user_request> and <task_details>:
    
    <update_request>
    {prompt}
    </update_request> 

    <task_details>
        <task_description>
        {design_plan.description_of_update}
        </task_description>

        {suggestion_comp_block}

        {suggestion_icon_block}

        {suggestion_wireframe_block}

    </task_details>
    """

    comp_model = ChatGoogleGenerativeAI(
        # model="gemini-2.5-pro-exp-03-25",
        model=model_mapping(state["model"]),
        api_key=state["gemini_api_key"],
        temperature=0.6,
        max_retries=2,
    )

    comp_Prompt.messages.append(HumanMessage(content=new_prompt))
    code_generated = comp_model.invoke(comp_Prompt)

    comp_Prompt.messages.append(AIMessage(content=code_generated.content))

    return {"history": comp_Prompt}


def generate_component_iter(state: genStateIter):
    comp_Prompt = state["history"].model_copy(deep=True)
    new_enh_prompt = state["enhance_prompt"]
    design_plan = state["design_plan"]
    prompt = new_enh_prompt.improved_request

    parsed_plan = gen_comp_task_iter_(prompt, design_plan)

    suggestion_comp_block, suggestion_icon_block, suggestion_wireframe_block = (
        parse_task_(parsed_plan)
    )

    new_prompt = f"""The user is requesting an update to the component you generated.
    Update the component based on <user_request> and <task_details>:
    
    <update_request>
    {prompt}
    </update_request> 

    <task_details>
        <task_description>
        {design_plan.description_of_update}
        </task_description>

        {suggestion_comp_block}

        {suggestion_icon_block}

        {suggestion_wireframe_block}

    </task_details>
    """

    comp_model = ChatGoogleGenerativeAI(
        # model="gemini-2.5-pro-exp-03-25",
        model=model_mapping(state["model"]),
        api_key=state["gemini_api_key"],
        temperature=0.6,
        max_retries=2,
    )

    comp_Prompt.messages.append(HumanMessage(content=new_prompt))
    code_generated = comp_model.invoke(comp_Prompt)

    comp_Prompt.messages.append(AIMessage(content=code_generated.content))

    return {"history": comp_Prompt, "generatedCode": code_generated}
