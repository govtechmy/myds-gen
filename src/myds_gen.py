# import os
import json
from langgraph.graph import StateGraph, START, END
# from langfuse.callback import CallbackHandler
from langchain_core.messages.ai import AIMessageChunk
from langchain_core.messages import messages_to_dict
from src.stages.design import validate, enhance, plan, wireframe
from src.stages.component_generation import generate_component
from src.stages.component_generation_iterate import (
    prompt_enhance_iter,
    design_update,
    generate_component_iter,
    generate_component_iter_stream,
)
from src.stages.build_context import generate
from src.util.rag import comp_rag, gen_comp_task
from src.util.langchain_schema import (
    designState,
    genState,
    genStateIter,
    iterInputState,
    learnState,
)

# os.environ["LANGSMITH_TRACING"] = os.environ["LANGSMITH_TRACING"]
# os.environ["LANGSMITH_API_KEY"] = os.environ["LANGSMITH_API_KEY"]
# os.environ["LANGSMITH_PROJECT"] = "jen"
# os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"

# langfuse_handler = CallbackHandler(
#     secret_key=os.environ["langchain_sk"],
#     public_key=os.environ["langchain_pk"],
#     host="https://cloud.langfuse.com",
# )


def context_builder(state: genState):
    return {
        "context": generate(
            state["component_task"],
            state["wireframe"].ascii_wireframe,
            state["gemini_api_key"],
        )
    }


def dumbcheck(state: designState):
    return state["valid"]


def design_plan_step(user_prompt: str, gemini_api_key: str):
    learner_graph = StateGraph(learnState)
    learner_graph.add_node("prompt_enhancement", enhance)
    learner_graph.add_node("component_rag", comp_rag)
    learner_graph.add_node("design_planning", plan)
    learner_graph.add_node("generate_task", gen_comp_task)
    learner_graph.add_node("wireframe_gen", wireframe)
    learner_graph.add_node("build_context", context_builder)
    learner_graph.add_edge(START, "prompt_enhancement")
    learner_graph.add_edge("prompt_enhancement", "component_rag")
    learner_graph.add_edge("component_rag", "design_planning")
    learner_graph.add_edge("design_planning", "generate_task")
    learner_graph.add_edge("generate_task", "wireframe_gen")
    learner_graph.add_edge("wireframe_gen", "build_context")
    learner = learner_graph.compile()

    root_graph = StateGraph(designState)
    root_graph.add_node("prompt_validation", validate)
    root_graph.add_node("learner", learner)
    root_graph.add_edge(START, "prompt_validation")
    root_graph.add_conditional_edges(
        "prompt_validation", dumbcheck, {True: "learner", False: END}
    )
    root_graph.add_edge("learner", END)
    workflow = root_graph.compile()

    state = workflow.invoke(
        {"user_prompt": user_prompt, "gemini_api_key": gemini_api_key},
        # config={"callbacks": [langfuse_handler]},
    )
    return state


def generate_component_step_Stream(design_state: designState):
    gen_graph = StateGraph(genState)
    gen_graph.add_node("generate_component", generate_component)
    gen_graph.add_edge(START, "generate_component")
    generator_workflow = gen_graph.compile()
    events = generator_workflow.stream(
        {
            "gemini_api_key": design_state["gemini_api_key"],
            "model": design_state["model"],
            "component_task": design_state["component_task"],
            "context": design_state["context"],
        },
        stream_mode=["messages", "values"],
        # config={"callbacks": [langfuse_handler], "run_name": "init_call_stream"},
    )
    for event_type, event in events:
        if event_type == "messages":
            chunk, metadata = event
            if isinstance(chunk, AIMessageChunk):
                if metadata["langgraph_node"] == "generate_component":
                    yield (
                        json.dumps(("chunk", chunk.content.replace("```", "//```")))
                        + "\n"
                    )

        elif event_type == "values":
            if "history" in event.keys():
                final_state = event
                yield (
                    json.dumps(
                        (
                            "final_state",
                            messages_to_dict(final_state["history"].to_messages()),
                        )
                    )
                    + "\n"
                )
    return


def generate_component_step(design_state: designState, stream=False):
    gen_graph = StateGraph(genState)
    gen_graph.add_node("generate_component", generate_component)
    gen_graph.add_edge(START, "generate_component")
    generator_workflow = gen_graph.compile()
    static_output = generator_workflow.invoke(
        {
            "gemini_api_key": design_state["gemini_api_key"],
            "model": design_state["model"],
            "component_task": design_state["component_task"],
            "context": design_state["context"],
            "stream": stream,
        },
        # config={"callbacks": [langfuse_handler], "run_name": "init_call_static"},
    )
    static_output = dict(static_output)
    static_output["history"] = messages_to_dict(static_output["history"].to_messages())
    return static_output


def generate_component_iteration(
    history: iterInputState, gemini_api_key: str, model: str
):
    history["gemini_api_key"] = gemini_api_key
    history["model"] = model
    iter_graph = StateGraph(genStateIter)
    iter_graph.add_node("prompt_enhancement", prompt_enhance_iter)
    iter_graph.add_node("design_update", design_update)
    iter_graph.add_node("generate_component", generate_component_iter)
    iter_graph.add_edge(START, "prompt_enhancement")
    iter_graph.add_edge("prompt_enhancement", "design_update")
    iter_graph.add_edge("design_update", "generate_component")
    iteration_workflow = iter_graph.compile()
    static_output = iteration_workflow.invoke(
        history,
        # config={"callbacks": [langfuse_handler], "run_name": "iter_call_static"},
    )
    static_output = dict(static_output)
    static_output["history"] = messages_to_dict(static_output["history"].to_messages())
    return static_output


def generate_component_iteration_Stream(
    history: iterInputState, gemini_api_key: str, model: str
):
    history["gemini_api_key"] = gemini_api_key
    history["model"] = model
    iter_graph = StateGraph(genStateIter)
    iter_graph.add_node("prompt_enhancement", prompt_enhance_iter)
    iter_graph.add_node("design_update", design_update)
    iter_graph.add_node("generate_component", generate_component_iter_stream)
    iter_graph.add_edge(START, "prompt_enhancement")
    iter_graph.add_edge("prompt_enhancement", "design_update")
    iter_graph.add_edge("design_update", "generate_component")
    iteration_workflow = iter_graph.compile()
    events = iteration_workflow.stream(
        history,
        stream_mode=["messages", "values"],
        # config={"callbacks": [langfuse_handler], "run_name": "iter_call_stream"},
    )
    events_passed = 0
    for event_type, event in events:
        if event_type == "messages":
            chunk, metadata = event
            if isinstance(chunk, AIMessageChunk):
                if metadata["langgraph_node"] == "generate_component":
                    yield (
                        json.dumps(("chunk", chunk.content.replace("```", "//```")))
                        + "\n"
                    )
                    events_passed += 1

        elif event_type == "values" and events_passed > 0:
            if "history" in event.keys():
                final_state = event
                yield (
                    json.dumps(
                        (
                            "final_state",
                            messages_to_dict(final_state["history"].to_messages()),
                        )
                    )
                    + "\n"
                )
    return
