import os
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

from src.stages import (
    design,
    component_generation,
    build_context,
    generation_validation,
    design_iterate,
    component_generation_iterate,
)
from src.util.api_schema import (
    BaseTask,
    BaseContext,
    ToGenerate,
    ComponentCode,
    ToPlanIterate,
    BaseTaskWthUpdate,
    ContextIterate,
    GenIterate,
)

load_dotenv()

api_key_header = APIKeyHeader(name="X-API-Key")

### Create FastAPI instance with custom docs and openapi url
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    api_keys = os.getenv("API_KEYS").split(",")
    if api_key_header in api_keys:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )

@app.get("/api/py/helloFastApi")
async def hello_fast_api():
    return {"message": "Hello from FastAPI"}


@app.post("/api/py/validate-new-prompt", tags=["New Component Generation"])
async def validate_new_prompt(prompt: str, api_key: str = Security(get_api_key)):
    return {"valid": design.prompt_validation(prompt)}


@app.post("/api/py/task_planning", tags=["New Component Generation"])
async def task_planning(prompt: str, api_key: str = Security(get_api_key)) -> BaseTask:
    design_data = design.design_planning(prompt)
    component_task = build_context.gen_comp_task(prompt, design_data)
    return component_task


@app.post("/api/py/wireframe_gen", tags=["New Component Generation"])
async def wireframe_gen(task: BaseTask, api_key: str = Security(get_api_key)) -> str:
    return design.design_layout(task.dict())


@app.post("/api/py/assemble_context", tags=["New Component Generation"])
async def assemble_context(task: BaseContext, api_key: str = Security(get_api_key)) -> str:
    return build_context.generate(task.task.dict(), task.wireframe)


@app.post("/api/py/generate_component", tags=["New Component Generation"])
async def generate_component(task: ToGenerate, api_key: str = Security(get_api_key)) -> str:
    return component_generation.generate(task.task.dict(), task.context)


@app.post("/api/py/validate_code", tags=["General"])
async def validate_code(component_str: ComponentCode, api_key: str = Security(get_api_key)) -> str:
    try:
        fixed_code = generation_validation.validate_full(component_str.tsx)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
    return fixed_code


@app.post("/api/py/task_planning_iter", tags=["Component Iteration"])
async def task_planning_iterate(task: ToPlanIterate, api_key: str = Security(get_api_key)) -> BaseTaskWthUpdate:
    # update_task_dict = update_task.dict()
    design_data = design_iterate.design_update(
        task.update_prompt, task.tsx, task.wireframe, task.task.dict()
    )
    return build_context.gen_comp_task_iter(
        task.update_prompt, design_data, task.task.dict()
    )


@app.post("/api/py/wireframe_iter", tags=["Component Iteration"])
async def wireframe_iterate(task: ContextIterate, api_key: str = Security(get_api_key)) -> str:
    return design_iterate.design_layout(task.task.dict(), task.wireframe)


@app.post("/api/py/assemble_context_iter", tags=["Component Iteration"])
async def assemble_context_iterate(task: ContextIterate, api_key: str = Security(get_api_key)) -> str:
    return build_context.generate_iter(task.task.dict(), task.wireframe)


@app.post("/api/py/generate_component_iterate", tags=["Component Iteration"])
async def generate_component_iterate(task: GenIterate, api_key: str = Security(get_api_key)) -> str:
    return component_generation_iterate.generate(
        task.task.dict(), task.context, task.tsx
    )
