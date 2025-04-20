import json
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from src.myds_gen import (
    design_plan_step,
    generate_component_step,
    generate_component_step_Stream,
    generate_component_iteration,
    generate_component_iteration_Stream,
)
from src.util.api_schema import iterationInput, iterationInputStream

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/init_prompt")
async def initialize_prompt(
    prompt: str,
    gemini_api_key: str = Header(None, alias="X-Gemini-API-Key"),
    model: str = Header(None, alias="X-Model-Type"),
) -> dict:
    if not gemini_api_key:
        raise HTTPException(
            status_code=400, detail="X-Gemini-API-Key header is required"
        )
    if not model:
        raise HTTPException(status_code=400, detail="X-Model-Type header is required")

    state = design_plan_step(prompt, gemini_api_key)
    if state["valid"]:
        run = generate_component_step(state)
        return {
            "generatedCode": run["generatedCode"].content.replace("```", "\\```"),
            "history": run["history"],
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid prompt")


@app.post("/init_prompt_stream")
async def initialize_prompt_stream(
    prompt: str,
    gemini_api_key: str = Header(None, alias="X-Gemini-API-Key"),
    model: str = Header(None, alias="X-Model-Type"),
) -> StreamingResponse:
    if not gemini_api_key:
        raise HTTPException(
            status_code=400, detail="X-Gemini-API-Key header is required"
        )
    if not model:
        raise HTTPException(status_code=400, detail="X-Model-Type header is required")
    state = design_plan_step(prompt, gemini_api_key)
    if state["valid"]:
        state["model"] = model
        return StreamingResponse(
            generate_component_step_Stream(state), media_type="text/event-stream"
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid prompt")


@app.post("/iteration")
async def iteration(iterationInput: iterationInput):
    message_class_map = {
        "system": SystemMessage,
        "human": HumanMessage,
        "ai": AIMessage,
    }

    hist_seq = [
        message_class_map[item_["type"]](**item_["data"])
        for item_ in iterationInput.history
        if item_.get("type") in message_class_map
        and isinstance(item_.get("data"), dict)
    ]
    history_ = {
        "history": ChatPromptValue(messages=hist_seq),
        "new_prompt": iterationInput.update_prompt,
    }

    run = generate_component_iteration(history_)
    return {
        "generatedCode": run["generatedCode"].content.replace("```", "//```"),
        "history": run["history"],
    }


@app.post("/iteration_stream")
async def iteration_stream(
    iterationInput: iterationInputStream,
    gemini_api_key: str = Header(None, alias="X-Gemini-API-Key"),
    model: str = Header(None, alias="X-Model-Type"),
) -> StreamingResponse:
    if not gemini_api_key:
        raise HTTPException(
            status_code=400, detail="X-Gemini-API-Key header is required"
        )
    if not model:
        raise HTTPException(status_code=400, detail="X-Model-Type header is required")
    # print(iterationInput.previous_state)
    # history_string = iterationInput.previous_state
    message_class_map = {
        "system": SystemMessage,
        "human": HumanMessage,
        "ai": AIMessage,
    }

    hist_seq = [
        message_class_map[item_["type"]](**item_["data"])
        for item_ in iterationInput.previous_state
        if item_.get("type") in message_class_map
        and isinstance(item_.get("data"), dict)
    ]
    history_ = {
        "history": ChatPromptValue(messages=hist_seq),
        "new_prompt": iterationInput.update_prompt,
    }
    return StreamingResponse(
        generate_component_iteration_Stream(history_, gemini_api_key, model),
        media_type="text/event-stream",
    )
